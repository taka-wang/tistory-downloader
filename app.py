import argparse
from datetime import date, datetime
import os
from urllib.parse import unquote, urlparse
from urllib.request import urlretrieve

import feedparser
import pytz
import requests
from bs4 import BeautifulSoup
import re
import json

CACHE_FILE = "downloaded_posts.json"

def extract_info_from_rss(rss_url, filter_date=None):
    """
    Extracts and filters information from an RSS feed.

    Parameters:
    - rss_url (str): The URL of the RSS feed.
    - filter_date (str): The date to filter entries after (format: YYYY/MM/DD).

    Returns:
    - list: A list of dictionaries containing 'url' and 'date' for each entry, sorted by date (newest to oldest).
    """
    feed = feedparser.parse(rss_url)

    if filter_date:
        filter_datetime = datetime.strptime(filter_date, "%Y/%m/%d").replace(tzinfo=pytz.UTC)
    else:
        filter_datetime = None

    items_info = [{'url': entry.link, 'date': datetime.strptime(entry.published, "%a, %d %b %Y %H:%M:%S %z").replace(tzinfo=pytz.UTC)} for entry in feed.entries if not filter_datetime or datetime.strptime(entry.published, "%a, %d %b %Y %H:%M:%S %z").replace(tzinfo=pytz.UTC) > filter_datetime]

    items_info = sorted(items_info, key=lambda x: x['date'], reverse=True)
    return items_info

def is_post_downloaded(url):
    """
    Checks if a post has already been downloaded based on the cache file.

    Parameters:
    - url (str): The URL of the post.

    Returns:
    - bool: True if the post has already been downloaded, False otherwise.
    """
    try:
        with open(CACHE_FILE, "r") as f:
            downloaded_posts = json.load(f)
            return url in downloaded_posts
    except FileNotFoundError:
        return False

def update_cache(url):
    """
    Updates the cache file to mark a post as downloaded.

    Parameters:
    - url (str): The URL of the post.

    Returns:
    - None
    """
    try:
        with open(CACHE_FILE, "r") as f:
            downloaded_posts = json.load(f)
    except FileNotFoundError:
        downloaded_posts = []

    downloaded_posts.append(url)

    with open(CACHE_FILE, "w") as f:
        json.dump(downloaded_posts, f, indent=2)

def download_images(url, items_info=None, output_folder='images'):
    """
    Downloads images from a given URL and saves them to the specified output folder.

    Parameters:
    - url (str): The URL of the webpage containing images.
    - items_info (list): List of dictionaries containing 'url' and 'date' for each entry (default: None).
    - output_folder (str): The folder to save downloaded images (default: 'images').

    Returns:
    - None
    """
    if is_post_downloaded(url):
        print(f"Post at {url} has already been downloaded. Skipping...")
        return

    try:
        response = requests.get(url)
        response.raise_for_status()
        html_code = response.text

        soup = BeautifulSoup(html_code, 'html.parser')
        figure_tags = soup.find_all('figure', class_='imageblock')

        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        index = extract_index_from_url(url)
        post_date = None

        if items_info:
            for item in items_info:
                if item['url'] == url:
                    post_date = item['date']
                    break

        if post_date is None:
            # If items_info is not provided or URL not found, use current date
            post_date = datetime.now(pytz.UTC)

        for i, figure_tag in enumerate(figure_tags, 1):
            image_url = figure_tag.find('span', attrs={'data-url': True}).get('data-url')
            image_path = os.path.join(output_folder, generate_filename(image_url, post_date, index, i))

            urlretrieve(image_url, image_path)
            print(f"Downloaded: {image_path}")

        # Update cache after successful download
        update_cache(url)

    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")

def extract_index_from_url(url):
    """
    Extracts the index from a URL.

    Parameters:
    - url (str): The URL containing the index.

    Returns:
    - str: The extracted index.
    """
    parsed_url = urlparse(url)
    path_segments = parsed_url.path.split('/')
    index = path_segments[-1] if path_segments[-1] else path_segments[-2]
    return index

def generate_filename(image_url, post_date, index, count):
    """
    Generates a new filename for a downloaded image.

    Parameters:
    - image_url (str): The URL of the downloaded image.
    - post_date (datetime): The date of the associated entry.
    - index (str): The index extracted from the URL.
    - count (int): The count of the image in the entry.

    Returns:
    - str: The generated filename.
    """
    parsed_url = urlparse(image_url)
    filename = os.path.basename(parsed_url.path)
    decoded_filename = unquote(filename)

    date_str = post_date.strftime("%Y-%m-%d")
    new_filename = f"{date_str}-{index}-{count}-{decoded_filename}"
    return new_filename

def complete_rss_url(url):
    """
    Completes the given URL by appending '/rss' if it doesn't end with it.

    Parameters:
    - url (str): The URL to complete.

    Returns:
    - str: The completed URL.
    """
    if not re.search(r'/rss$', url):
        return url.rstrip('/') + '/rss'
    return url

def main():
    """
    Main function to extract and download images from an RSS feed.
    """
    parser = argparse.ArgumentParser(description="Extract and download images from an RSS feed.")
    parser.add_argument("-i", "--url", default="https://iuedelweiss.tistory.com", help="The URL of the RSS feed (default: https://iuedelweiss.tistory.com)")
    parser.add_argument("-f", "--filter", help="Filter entries after this date (format: YYYY/MM/DD)")
    parser.add_argument("-o", "--output", default="images", help="The output folder for downloaded images (default: 'images')")

    args = parser.parse_args()

    # Complete the URL by appending '/rss' if needed
    rss_url = complete_rss_url(args.url)

    items_info = extract_info_from_rss(rss_url, args.filter)

    for item in items_info:
        print("URL:", item['url'])
        print("Date:", item['date'])
        print("-" * 30)
        download_images(item['url'], items_info, args.output)

if __name__ == "__main__":
    main()
