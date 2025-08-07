"""Scrapes jobs from the URL."""

import csv
import json
import requests
from bs4 import BeautifulSoup


def load_settings():
    """Loads settings from config.json."""
    try:
        with open('config.json', 'r', encoding='utf-8') as f:
            settings = json.load(f)
        return settings
    except FileNotFoundError:
        print("Error: config.json not found. Please create it.")
        return None


def scrape_jobs(URL):
    '''Fetches and parses job listings from the given URL.'''
    try:
        r = requests.get(URL, timeout=4)
        r.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching URL: {e}")
        return []

    soup = BeautifulSoup(r.text, "html.parser")
    soup = BeautifulSoup(r.text, "html.parser")
    results = soup.find(id="ResultsContainer")
    if results is None:
        print("Error: Could not find the results container in the page.")
        return []
    job_elements = results.find_all("div", class_="card-content")
    return job_elements


def extract_jobs(job_elements, keywords, limit):
    '''Extracts jobs with desired keywords, respecting the limit.'''
    jobs_data = []
    for job_element in job_elements:
        title_element = job_element.find("h2", class_="title")
        company_element = job_element.find("h3", class_="company")
        location_element = job_element.find("p", class_="location")

        if not all([title_element, company_element, location_element]):
            continue

        title = title_element.text.strip()

        should_add = any(keyword.lower() in title.lower()
                         for keyword in keywords) or not keywords
        if should_add:
            company = company_element.text.strip()
            location = location_element.text.strip()
            link_url = job_element.find_all("a")[1]["href"]

            jobs_data.append({
                "Title": title,
                "Company": company,
                "Location": location,
                "Link": link_url,
            })
            if limit > 0 and len(jobs_data) >= limit:
                break

    return jobs_data


def save_to_csv(jobs_data, filename):
    '''Saves the gathered data to a CSV file.'''
    if not jobs_data:
        print("No jobs matched the criteria. There is nothing to save.")
        return

    keys = jobs_data[0].keys()

    with open(filename, "w", newline="", encoding='utf-8') as output_file:
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(jobs_data)

    print(
        f"Scraping has been completed with {len(jobs_data)} result(s). Data saved to {filename}.")


def main():
    '''Main function of the scraper'''
    settings = load_settings()
    if not settings:
        return
    URL = "https://realpython.github.io/fake-jobs/"

    all_job_elements = scrape_jobs(URL)

    filtered_job_elements = extract_jobs(
        all_job_elements, settings["filter_keywords"], settings["number_of_scrapes"])

    save_to_csv(filtered_job_elements, settings["output_filename"])


if __name__ == "__main__":
    main()
