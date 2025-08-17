import json
import logging
from os import makedirs
from os.path import isdir, isfile

import requests
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def process_company(company_url):
    filename = './json_/' + company_url.split('/')[-1] + '.json'
    # if isfile(filename):
    #     logging.info(f"File {filename} already exists, skipping processing.")
    #     return
    logging.info(f"Processing company URL: {company_url}")
    html_content = getRes(company_url)
    if not html_content:
        logging.error(f"Failed to retrieve content from {company_url}")
        return
    soup = BeautifulSoup(html_content, 'html.parser')
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
    data_cfemail = soup.find('a', {"data-cfemail":True})
    if data_cfemail:
        encoded_email = data_cfemail['data-cfemail']
        decoded_email = cfDecodeEmail(encoded_email)
        data['email'] = decoded_email
    extra_info = soup.find('div',{ 'class': 'extra-info'})
    if extra_info:
        for item in extra_info.find_all('div', {'class': 'info'}):
            label = item.find('span', {'class': 'label'})
            value = item.find('span', {'class': 'value'})
            if label and value:
                key = label.get_text(strip=True).lower().replace(' ', '_')
                data[key] = value.get_text(strip=True)
    # logging.info(f"Extracted data: {data}")
    print(json.dumps(data, indent=4, ensure_ascii=False))
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False)


def cfDecodeEmail(encodedString):
    r = int(encodedString[:2], 16)
    email = ''.join([chr(int(encodedString[i:i + 2], 16) ^ r) for i in range(2, len(encodedString), 2)])
    return email


def getRes(url):
    logging.info(f"Fetching URL: {url}")
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        logging.error(f"Error fetching URL {url}: {e}")
        return None


def main():
    makedirs('json_', exist_ok=True)
    process_company("https://www.floridanegocio.com/company/497068/Appliances_Repair_Zayas_LLC")


if __name__ == '__main__':
    main()
