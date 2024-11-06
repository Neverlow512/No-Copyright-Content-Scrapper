# scrapers/pexels_scraper.py
import requests
import os
import logging
import json
import math

def scrape(args, config):
    api_key = config['api_keys']['pexels']
    if not api_key:
        logging.error("Pexels API key is missing.")
        return

    headers = {'Authorization': api_key}
    keywords = '+'.join(args['keywords'])
    categories = '+'.join(args['categories'])
    query = f"{keywords}+{categories}" if categories else keywords
    content_type = 'photos' if args['content_type'] == '1' else 'videos'
    per_page = 80  # Maximum allowed per Pexels API
    total_results = args['num_results']
    total_pages = math.ceil(total_results / per_page)

    for page in range(1, total_pages + 1):
        # Correct the API endpoint URLs
        if content_type == 'photos':
            url = f"https://api.pexels.com/v1/search?query={query}&per_page={per_page}&page={page}"
        else:
            url = f"https://api.pexels.com/videos/search?query={query}&per_page={per_page}&page={page}"

        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            logging.error(f"Failed to fetch data from Pexels: {response.status_code}")
            return

        data = response.json()
        save_content(data, args, config, 'pexels', content_type)

        # Break if we've collected enough results
        if page * per_page >= total_results:
            break

def save_content(data, args, config, website, content_type):
    db_path = config['database_path']
    metadata_path = config.get('metadata_path', 'metadata')
    quality = args['quality']
    fmt = args['format']
    fmt_sanitized = args['format_sanitized']
    keywords = '_'.join(args['keywords'])
    categories = '_'.join(args['categories']) if args['categories'] else 'All'

    # Construct the directory path
    dir_path = os.path.join(db_path, website, keywords, categories, content_type, quality, fmt_sanitized)
    os.makedirs(dir_path, exist_ok=True)

    # Prepare metadata list
    metadata_list = []

    items = data.get('photos', []) if content_type == 'photos' else data.get('videos', [])

    for item in items:
        if content_type == 'photos':
            image_url = item['src']['original']
            file_name = os.path.join(dir_path, f"{item['id']}.jpg")
            download_file(image_url, file_name)
            file_url = image_url
        else:
            # Select the video file matching the desired quality if available
            video_files = item['video_files']
            video_url = None
            for vf in video_files:
                aspect_ratio = vf['width'] / vf['height']
                desired_aspect = 16/9 if fmt == '16:9' else 9/16
                if vf['quality'] == quality.lower() and abs(aspect_ratio - desired_aspect) < 0.01:
                    video_url = vf['link']
                    break
            if not video_url and video_files:
                # Fallback to the first available video
                video_url = video_files[0]['link']
            if not video_url:
                continue  # Skip if no video URL is found
            file_name = os.path.join(dir_path, f"{item['id']}.mp4")
            download_file(video_url, file_name)
            file_url = video_url

        # Collect metadata
        metadata = {
            'file_name': file_name,
            'file_url': file_url,
            'website': website,
            'keywords': args['keywords'],
            'categories': args['categories'],
            'content_type': content_type,
            'quality': quality,
            'format': fmt,
            'id': item['id'],
            'original_url': item['url']
        }
        metadata_list.append(metadata)

    # Save metadata to JSON file
    metadata_file = os.path.join(metadata_path, f"{website}_{keywords}_{categories}_{content_type}_{quality}_{fmt_sanitized}.json")
    os.makedirs(metadata_path, exist_ok=True)
    with open(metadata_file, 'a') as f:  # Append to the file for multiple pages
        json.dump(metadata_list, f, indent=4)
    logging.info(f"Metadata saved to {metadata_file}")

def download_file(url, file_name):
    try:
        if not os.path.exists(file_name):
            response = requests.get(url, stream=True)
            with open(file_name, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            logging.info(f"Downloaded {file_name}")
        else:
            logging.info(f"File already exists: {file_name}")
    except Exception as e:
        logging.error(f"Failed to download {url}: {e}")
