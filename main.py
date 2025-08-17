# -*- coding: utf-8 -*-
import json
import logging
from csv import DictWriter
from glob import glob
from os import makedirs
from os.path import isfile
from random import shuffle
from threading import Thread, Semaphore
from time import sleep

import requests
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
base_url = 'https://www.floridanegocio.com'
posts_per_page=20
threads_count=10
semaphore = Semaphore(threads_count)
def process_company(company_url):
    filename = './json_/' + company_url.split('/')[-1] + '.json'
    if isfile(filename):
        logging.info(f"File {filename} already exists, skipping processing.")
        return
    logging.info(f"Processing company URL: {company_url}")
    soup = getSoup(company_url)
    if not soup:
        logging.error(f"Failed to retrieve or parse the page: {company_url}")
        return
    script = soup.find('script', type='application/ld+json')
    if not script:
        logging.error("No script tag with type 'application/ld+json' found.")
        return
    script_json = json.loads(script.string)
    data = {
        "@id": script_json.get("@id", ""),
        "name": script_json.get("name", ""),
        "image": script_json.get("image", ""),
        "address_streetAddress": script_json.get("address", {}).get("streetAddress", ""),
        "address_addressLocality": script_json.get("address", {}).get("addressLocality", ""),
        "address_addressRegion": script_json.get("address", {}).get("addressRegion", ""),
        "address_addressCountry": script_json.get("address", {}).get("addressCountry", ""),
        "telephone": script_json.get("telephone", ""),
        "url": script_json.get("url", ""),
        "geo_latitude": script_json.get("geo", {}).get("latitude", ""),
        "geo_longitude": script_json.get("geo", {}).get("longitude", "")
    }
    data_cfemail = soup.find('a', {"data-cfemail": True})
    if data_cfemail:
        encoded_email = data_cfemail['data-cfemail']
        decoded_email = cfDecodeEmail(encoded_email)
        data['email'] = decoded_email
    extra_info = soup.find('div', {'class': 'extra_info'})
    if extra_info:
        for item in extra_info.find_all('div', {'class': 'info'}):
            label = item.find('div', {'class': 'label'})
            label_text = label.get_text(strip=True)
            value = item.text.replace(label_text, '').strip()
            if value == '[email protected]':
                continue
            data[label_text] = value
    text_desc = soup.find('div', {'class': 'text desc'})
    if text_desc:
        data['description'] = text_desc.get_text(strip=True)
    else:
        data['description'] = ''
    tags = soup.find('div', {'class': 'tags'})
    if tags:
        data['tags'] = ", ".join([tag.get_text(strip=True) for tag in tags.find_all('a')])
    logging.info(f"Extracted data: {data}")
    # print(json.dumps(data, indent=4, ensure_ascii=False))
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False)



def process_category(cat_url, category_name, category_count):
    threads=[]
    total_pages=int(category_count.replace(",","")) // posts_per_page + 1
    pages = list(range(1, total_pages + 1))
    shuffle(pages)
    logging.info(f"Processing category: {category_name} with {category_count} companies across {total_pages} pages.")
    logging.info(f"Category URL: {base_url}{cat_url}")
    for page in pages:
        category_url = f"{base_url}{cat_url}/{page}"
        logging.info(f"Processing category ({category_name}) ({page}/{total_pages}) {category_url}")
        soup = getSoup(category_url)
        if not soup:
            logging.error(f"Failed to retrieve or parse the page: {category_url}")
            return
        companies = soup.find_all('div', {'class': 'company'})
        for company in companies:
            a = company.find('a')
            if a and 'href' in a.attrs:
                company_url = a['href']
                # process_company(f"{base_url}{company_url}")
                thread = Thread(target=process_company, args=(f"{base_url}{company_url}",))
                thread.start()
                threads.append(thread)
        for thread in threads:
            thread.join()

def generate_csv():
    files = glob('json_/*.json')
    with open('floridanegocio.csv', 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['@id', 'name', 'image', 'address_streetAddress', 'address_addressLocality',
                      'address_addressRegion', 'address_addressCountry', 'telephone', 'url',
                      'geo_latitude', 'geo_longitude', 'email', 'description', 'tags',
                      'Empleados','Establecimiento anual', 'Gerente de empresa','Persona de contacto']
        writer = DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for file in files:
            with open(file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                writer.writerow(data)
def main():
    logo()
    makedirs('json_', exist_ok=True)
    logging.info(f"Starting to process business directory categories from {base_url}/browse-business-directory")
    url = f'{base_url}/browse-business-directory'
    soup = getSoup(url)
    icats = soup.find_all('ul', {'class': 'icats'})
    shuffle(icats)
    logging.info(f"Found {len(icats)} categories to process.")
    for icat in icats:
        for li in icat.find_all('li'):
            a = li.find('a')
            if a and 'href' in a.attrs:
                category_url = a['href']
                cat_text = a.get_text(strip=True)
                cat_count = a.find('span').text
                cat_name = cat_text.replace(cat_count, '_')
                process_category(category_url, cat_name, cat_count)
                generate_csv()




def getRes(url):
    # logging.info(f"Fetching URL: {url}")
    try:
        with semaphore:
            response = requests.get(url)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        logging.error(f"Error fetching URL {url}: {e}")
        return None


def getSoup(url):
    html_content = getRes(url)
    if not html_content:
        return None
    return BeautifulSoup(html_content, 'html.parser')

def cfDecodeEmail(encodedString):
    r = int(encodedString[:2], 16)
    email = ''.join([chr(int(encodedString[i:i + 2], 16) ^ r) for i in range(2, len(encodedString), 2)])
    return email
def logo():
    print(rf"""
  __  _               _      _                                          _        
 / _|| |             (_)    | |                                        (_)       
| |_ | |  ___   _ __  _   __| |  __ _  _ __    ___   __ _   ___    ___  _   ___  
|  _|| | / _ \ | '__|| | / _` | / _` || '_ \  / _ \ / _` | / _ \  / __|| | / _ \ 
| |  | || (_) || |   | || (_| || (_| || | | ||  __/| (_| || (_) || (__ | || (_) |
|_|  |_| \___/ |_|   |_| \__,_| \__,_||_| |_| \___| \__, | \___/  \___||_| \___/ 
                                                     __/ |                       
                                                    |___/                        
==================================================================================       
        floridanegocio.com scraper by https://github.com/evilgenius786          
==================================================================================
[+] JSON Based
[+] Multi-threaded
[+] Randomized Category Processing
[+] Email Obfuscation Decoding
[+] CSV Generation
[+] Data Extraction from JSON-LD
[+] BeautifulSoup for HTML Parsing
[+] Requests for HTTP Requests
[+] Logging for Debugging and Information

""")

    print(rf"""
  _____________________________________________________________________________________
 |                                                                                     |
 |   This script is designed to scrape business directory data from floridanegocio.com |
 |   and save it in JSON files, with an option to generate a CSV file.                 |
 |   Ensure you have the necessary permissions to scrape the website.                  |
 |                                                                                     |
 |   Usage: python main.py                                                             |
 |                                                                                     |
 |   For more information, visit: https://github.com/evilgenius786                     |
 |_____________________________________________________________________________________|        

""")
    sleep(1)

if __name__ == '__main__':
    main()
