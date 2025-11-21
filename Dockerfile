# Use an official Python runtime as the base image
FROM python:3.9-slim-buster

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your app's code into the container
COPY . .

# Expose the port your app will run on
EXPOSE 8000

# Run your app
CMD ["python", "hudle_loop_all_city_to_generate_venue_URL.py","hudle_next_data_bulk_scraper_retry.py"]
