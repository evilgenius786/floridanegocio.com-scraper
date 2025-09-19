# FloridaNegocio Business Directory Scraper

This project is a Python-based scraper for [floridanegocio.com](https://www.floridanegocio.com).  
It collects company information from the business directory, saves each company’s details as JSON, and compiles all results into a CSV file.

---

## Features

- Scrapes business categories and company pages.
- Extracts structured business data from embedded `application/ld+json` scripts.
- Decodes Cloudflare-protected email addresses.
- Saves each company as a JSON file in the `json_` folder.
- Exports all collected data into a single CSV file (`floridanegocio.csv`).
- Uses multithreading for faster scraping.
- Includes logging for progress and error tracking.

---

## Extracted Fields

Each company entry may include:

- `@id`  
- `name`  
- `image`  
- `address_streetAddress`  
- `address_addressLocality`  
- `address_addressRegion`  
- `address_addressCountry`  
- `telephone`  
- `url`  
- `geo_latitude`  
- `geo_longitude`  
- `email` (decoded if Cloudflare-protected)  
- `description`  
- `tags`  
- Additional fields like **Empleados**, **Establecimiento anual**, **Gerente de empresa**, **Persona de contacto**, **Registro del IVA**

---

## Requirements

- Python 3.8+
- Packages listed in `requirements.txt`:

```
requests
beautifulsoup4
wakepy
```

---

## Installation

1. Clone this repository or copy the script.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

---

## Usage

Run the scraper with:

```bash
python scraper.py
```

### Workflow
1. The script creates a `json_` folder if it does not exist.
2. It scrapes all business categories from  
   [https://www.floridanegocio.com/browse-business-directory](https://www.floridanegocio.com/browse-business-directory).
3. Each company’s details are saved as an individual JSON file inside `json_/`.
4. After scraping, all JSON data is combined into `floridanegocio.csv`.

---

## Output

- **JSON files:** Stored in the `json_` directory.  
- **CSV file:** `floridanegocio.csv` containing all extracted company data.  

---

## Logging

The script logs its progress and errors to the console, including:

- Category and page being processed  
- Company URLs being scraped  
- Warnings if files already exist  
- Errors if pages fail to load or parse  

---

## Notes

- Scraping large datasets may take time depending on network conditions.  
- The script uses multithreading (`threads_count = 10`) to improve performance.  
- If a JSON file is empty or corrupted, it is skipped or removed during CSV generation.  
