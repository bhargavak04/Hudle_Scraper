#!/bin/bash

echo "Running first script..."
python hudle_loop_all_city_to_generate_venue_URL.py

echo "First script finished. Running second script..."
python hudle_next_data_bulk_scraper_retry.py

echo "All tasks completed. Keeping container alive..."
tail -f /dev/null

