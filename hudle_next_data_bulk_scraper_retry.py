    
import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
import time
import re

def extract_contact_from_html(html_content):
    """Extract contact information from HTML with better filtering"""
    contact_info = []
    
    # More specific phone patterns for Indian numbers
    phone_patterns = [
        r'\+91[\s\-]?[6-9]\d{9}',  # Indian mobile with +91
        r'[6-9]\d{9}',  # 10-digit mobile starting with 6-9
        r'\b\d{2,4}[\s\-]?\d{6,8}\b',  # Landline numbers
    ]
    
    # Extract phone numbers with better filtering
    for pattern in phone_patterns:
        matches = re.findall(pattern, html_content)
        for match in matches:
            clean_match = re.sub(r'[^\d]', '', match)
            
            # Filter out obvious non-phone numbers
            if (len(clean_match) == 10 and 
                clean_match.startswith(('6', '7', '8', '9')) and
                not any(x in match for x in ['1756', '1758', '1759', '1521', '1583', '1723']) and  # Filter tracking numbers
                not any(x in match for x in ['2025', '2024', '2023', '2019']) and  # Filter dates
                not any(x in match for x in ['8541837710', '85418377102']) and  # Filter system numbers
                clean_match not in ['7565778780', '7565779328', '7580363688', '7580363791', '7580363850', '7580363891']):  # Filter more system numbers
                
                contact_info.append(match.strip())
    
    # Remove duplicates while preserving order
    seen = set()
    unique_contacts = []
    for contact in contact_info:
        if contact not in seen:
            seen.add(contact)
            unique_contacts.append(contact)
    
    return unique_contacts

def extract_venue_details_from_next_data(url, max_retries=3):
    headers = {"User-Agent": "Mozilla/5.0"}
    for attempt in range(max_retries):
        try:
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            break  # Success
        except requests.exceptions.RequestException as e:
            print(f"⚠️ Attempt {attempt + 1} failed for {url}: {e}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
            else:
                return {"Venue URL": url, "Error": str(e)}

    soup = BeautifulSoup(response.text, "html.parser")
    script = soup.find("script", {"id": "__NEXT_DATA__", "type": "application/json"})
    if not script:
        return {"Venue URL": url, "Error": "No __NEXT_DATA__ tag found"}

    try:
        json_data = json.loads(script.string)
        venue = json_data["props"]["pageProps"]["venueDetails"]
    except Exception as e:
        return {"Venue URL": url, "Error": str(e)}
    
    # Extract contact information from HTML
    html_contacts = extract_contact_from_html(response.text)

    data = {
        "Venue URL": url,
        "name": venue.get("name"),
        "description": venue.get("description"),
        "address": venue.get("address"),
        "short_address": venue.get("short_address"),
        "closest_metro": venue.get("closest_metro"),
        "latitude": venue.get("latitude"),
        "longitude": venue.get("longitude"),
        "phone": venue.get("phone"),
        "contact_phone": venue.get("contact_phone"),
        "telephone": venue.get("telephone"),
        "mobile": venue.get("mobile"),
        "contact_number": venue.get("contact_number"),
        "html_contacts": ", ".join(html_contacts) if html_contacts else None,
        "available_time_period": venue.get("available_time_period"),
        "payment_options": venue.get("payment_options"),
        "tax": venue.get("tax"),
        "rating_count": venue.get("rating_count"),
        "rating": venue.get("rating"),
        "is_approved": venue.get("is_approved"),
        "view_count": venue.get("view_count"),
        "lead_count": venue.get("lead_count"),
        "is_interested": venue.get("is_interested"),
        "pay_at_venue": venue.get("pay_at_venue"),
        "is_hudle_exclusive": venue.get("is_hudle_exclusive"),
        "price_onwards": venue.get("price_onwards"),
        "offer_text": venue.get("offer_text"),
        "is_cancellable": venue.get("is_cancellable"),
        "is_bookable": venue.get("is_bookable"),
        "is_coaching": venue.get("is_coaching"),
        "is_daily_view_enabled": venue.get("is_daily_view_enabled"),
        "credit_plans_count": venue.get("credit_plans_count"),
        "is_outbound_venue": venue.get("is_outbound_venue"),
        "created_at": venue.get("created_at"),
        "updated_at": venue.get("updated_at"),
        "city_id": venue.get("city", {}).get("id"),
        "city_name": venue.get("city", {}).get("name"),
        "city_latitude": venue.get("city", {}).get("latitude"),
        "city_longitude": venue.get("city", {}).get("longitude"),
        "extra_features": json.dumps(venue.get("extra_features", []), ensure_ascii=False),
        "sports": json.dumps(venue.get("sports", []), ensure_ascii=False),
        "activities": json.dumps(venue.get("activities", []), ensure_ascii=False)
    }
    return data

def main():
    excel_file = r"C:\Users\bharg\Downloads\Sportomic_AI\Received\hudle_all_city_venue_urls.xlsx"
    df = pd.read_excel(excel_file, usecols=[1], engine="openpyxl").dropna().drop_duplicates()
    df.columns = ["Venue URL"]

    all_data = []
    for idx, row in df.iterrows():
        url = row["Venue URL"]
        result = extract_venue_details_from_next_data(url)
        all_data.append(result)
        
        # Extract and log contact information
        contact_info = []
        if result.get("phone"):
            contact_info.append(f"Phone: {result['phone']}")
        if result.get("contact_phone"):
            contact_info.append(f"Contact Phone: {result['contact_phone']}")
        if result.get("telephone"):
            contact_info.append(f"Telephone: {result['telephone']}")
        if result.get("mobile"):
            contact_info.append(f"Mobile: {result['mobile']}")
        if result.get("contact_number"):
            contact_info.append(f"Contact Number: {result['contact_number']}")
        if result.get("html_contacts"):
            contact_info.append(f"HTML Contacts: {result['html_contacts']}")
        
        contact_str = " | ".join(contact_info) if contact_info else "No contact info found"
        print(f"Processed {idx + 1}: {url}")
        print(f"Contact: {contact_str}")
        time.sleep(1)

        if (idx + 1) % 20 == 0:
            pd.DataFrame(all_data).to_excel("hudle_venue_next_data_autosave.xlsx", index=False, engine="openpyxl")
            print(f"💾 Auto-saved after {idx + 1} venues")

    pd.DataFrame(all_data).to_excel("hudle_venue_next_data_final.xlsx", index=False, engine="openpyxl")
    print("✅ Data saved to 'hudle_venue_next_data_final.xlsx'")

if __name__ == "__main__":
    main()
