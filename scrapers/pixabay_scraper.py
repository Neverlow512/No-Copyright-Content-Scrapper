# scrapers/pixabay_scraper.py
import requests
import os
import logging
import json
import math

def scrape(args, config):
    api_key = config['api_keys']['pixabay']
    if not api_key:
        logging.error("Pixabay API key is missing.")
        return

    keywords = '+'.join(args['keywords'])
    # Pixabay supports specific categories
    allowed_categories = [
        'fashion', 'nature', 'backgrounds', 'science', 'education', 'people', 'feelings',
        'religion', 'health', 'places', 'animals', 'industry', 'computer', 'food', 'sports',
        'transportation', 'travel', 'buildings', 'business', 'music'
    ]
    categories_filtered = [cat.lower() for cat in args['categories'] if cat.lower() in allowed_categories]
    categories = ','.join(categories_filtered)
    query = f"{keywords}"
    content_type = 'image' if args['content_type'] == '1' else 'video'
    per_page = 200  # Maximum allowed per Pixabay API
    total_results = args['num_results']
    total_pages = math.ceil(total_results / per_page)

    for page in range(1, total_pages + 1):
        if content_type == 'image':
            url = f"https://pixabay.com/api/?key={api_key}&q={query}&image_type=photo&per_page={per_page}&page={page}"
            if categories:
                url += f"&category={categories}"
        else:
            url = f"https://pixabay.com/api/videos/?key={api_key}&q={query}&per_page={per_page}&page={page}"
            if categories:
                url += f"&category={categories}"

        response = requests.get(url)
        if response.status_code != 200:
            logging.error(f"Failed to fetch data from Pixabay: {response.status_code}")
            return

        data = response.json()
        if not data.get('hits'):
            logging.info(f"No results found for query: {query} on page {page}")
            break

        save_content(data, args, config, 'pixabay', content_type)

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

    items = data.get('hits', [])

    for item in items:
        if content_type == 'image':
            image_url = item['largeImageURL']
            file_extension = os.path.splitext(image_url)[1]
            file_name = os.path.join(dir_path, f"{item['id']}{file_extension}")
            download_file(image_url, file_name)
            file_url = image_url
        else:
            # Select video with desired quality
            videos = item['videos']
            video_url = None
            quality_levels = ['large', 'medium', 'small', 'tiny']
            for ql in quality_levels:
                if ql in videos:
                    video_url = videos[ql]['url']
                    break
            if not video_url:
                continue  # Skip if no video URL is found
            file_extension = os.path.splitext(video_url)[1]
            file_name = os.path.join(dir_path, f"{item['id']}{file_extension}")
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
            'page_url': item['pageURL']
        }
        metadata_list.append(metadata)

    if not metadata_list:
        logging.info(f"No valid items found to save for query: {keywords}")
        return

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
            if response.status_code == 200:
                with open(file_name, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                logging.info(f"Downloaded {file_name}")
            else:
                logging.error(f"Failed to download {url}: Status code {response.status_code}")
        else:
            logging.info(f"File already exists: {file_name}")
    except Exception as e:
        logging.error(f"Failed to download {url}: {e}")
