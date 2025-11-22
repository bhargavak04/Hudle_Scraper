import requests
import json
import pandas as pd
import logging
import time
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from pathlib import Path

# Setup logging
# searching for all venue URLs for each city from 1 to 120 in Hudle
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def extract_all_city_venues(start_city=0, end_city=150, output_file='hudle_all_city_venue_urls.xlsx'):
    session = requests.Session()
    retries = Retry(total=3, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
    session.mount('https://', HTTPAdapter(max_retries=retries))

    base_url = "https://api.hudle.in/api/v1/venue-search"
    all_venues = []

    # Resume if file already exists
    file_path = Path(output_file)
    if file_path.exists():
        existing_df = pd.read_excel(file_path)
        all_venues = existing_df.to_dict(orient="records")
        completed_city_ids = set(existing_df["City ID"])
        logging.info(f"Resuming from existing file with {len(existing_df)} entries")
    else:
        completed_city_ids = set()

    for city_id in range(start_city, end_city + 1):
        if city_id in completed_city_ids:
            logging.info(f"City ID {city_id} already processed. Skipping.")
            continue

        params = {
            "per_page": 6,
            "cityId": city_id,
            "api_secret": "hudle-api1798@prod",
            "scope": 0,
            "vendor_id": 40,
            "device": 1,
            "client": "consumer",
            "device_id": "754158",
            "page": 1,
            "venueName": "",
            "preferred_sports": ""
        }

        headers = {
            "User-Agent": "Mozilla/5.0",
            "Accept": "application/json",
            "Api-Secret": "hudle-api1798@prod",
            "x-app-id": "25010064645373613700053736864153624",
        }

        logging.info(f"Scraping City ID {city_id}")
        city_venues = []
        try:
            while True:
                response = session.get(base_url, params=params, headers=headers, timeout=10)
                response.raise_for_status()
                data = response.json()

                if not data.get("data"):
                    logging.info(f"No data for City ID {city_id}, Page {params['page']}")
                    break

                for venue in data["data"]:
                    share_url = venue.get("share_url")
                    if share_url and share_url.startswith("https://hudle.in/venues/"):
                        city_venues.append({
                            "City ID": city_id,
                            "Venue URL": share_url,
                            "Venue ID": venue.get("id", "N/A"),
                            "Name": venue.get("name", "N/A"),
                            "Sports": ", ".join([sport["name"] for sport in venue.get("sports", [])]),
                            "Rating": venue.get("rating", "N/A"),
                            "Price Onwards": venue.get("price_onwards", "N/A")
                        })

                total_pages = data["meta"]["pagination"]["total_pages"]
                logging.info(f"City {city_id} - Page {params['page']}/{total_pages} | Collected {len(city_venues)} venues so far")
                params["page"] += 1
                time.sleep(1)

        except Exception as e:
            logging.error(f"Error in City ID {city_id}: {str(e)}")

        # Append city data and save
        all_venues.extend(city_venues)
        df = pd.DataFrame(all_venues)
        df.to_excel(output_file, index=False)
        logging.info(f"✅ Saved data for City ID {city_id} ({len(city_venues)} venues) | Total so far: {len(df)}")

if __name__ == "__main__":
    extract_all_city_venues()
