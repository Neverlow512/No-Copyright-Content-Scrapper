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
    content_type = 'photos' if args['content_type'] == '1' else 'videos'
    per_page = 80  # Maximum allowed per Pexels API
    fmt = args['format']
    fmt_sanitized = args['format_sanitized']
    quality = args['quality'].lower()

    for keyword_set in args['keyword_sets']:
        # Build the query using keywords, categories, and styles
        query_parts = [keyword_set]
        if args['categories']:
            query_parts += args['categories']
        if args['styles']:
            query_parts += args['styles']
        query = '+'.join(query_parts)

        total_downloaded = 0
        page = 1

        while total_downloaded < args['num_results']:
            if content_type == 'photos':
                url = f"https://api.pexels.com/v1/search?query={query}&per_page={per_page}&page={page}"
            else:
                url = f"https://api.pexels.com/videos/search?query={query}&per_page={per_page}&page={page}"

            response = requests.get(url, headers=headers)
            if response.status_code != 200:
                logging.error(f"Failed to fetch data from Pexels: {response.status_code}")
                break  # Proceed to next keyword set

            data = response.json()
            items = data.get('photos', []) if content_type == 'photos' else data.get('videos', [])

            if not items:
                logging.info(f"No results found for query: {query} on page {page}")
                break

            num_to_download = args['num_results'] - total_downloaded
            save_content(items, args, config, 'pexels', content_type, keyword_set, num_to_download)
            total_downloaded += min(len(items), num_to_download)

            if total_downloaded >= args['num_results']:
                break

            page += 1

def save_content(items, args, config, website, content_type, keyword_set, num_to_download):
    db_path = config['database_path']
    metadata_path = config.get('metadata_path', 'metadata')
    quality = args['quality']
    fmt = args['format']
    fmt_sanitized = args['format_sanitized']
    categories = '_'.join(args['categories']) if args['categories'] else 'All'
    styles = '_'.join(args['styles']) if args['styles'] else 'All'

    # Sanitize keyword set for directory name
    keyword_dir = keyword_set.replace(' ', '_')

    # Construct the directory path
    dir_path = os.path.join(db_path, website, keyword_dir, categories, styles, content_type, quality, fmt_sanitized)
    os.makedirs(dir_path, exist_ok=True)

    # Prepare metadata list
    metadata_list = []
    downloaded_count = 0

    for item in items:
        if downloaded_count >= num_to_download:
            break

        if content_type == 'photos':
            image_url = item['src']['original']
            file_extension = os.path.splitext(image_url)[1].split('?')[0] or '.jpg'
            file_name = os.path.join(dir_path, f"{item['id']}{file_extension}")
            download_success = download_file(image_url, file_name)
            file_url = image_url
        else:
            # Select the video file matching the desired quality and format
            video_files = item['video_files']
            video_url = None
            for vf in video_files:
                aspect_ratio = vf['width'] / vf['height']
                desired_aspect = 16/9 if fmt == '16:9' else 9/16
                if vf['quality'] == quality and abs(aspect_ratio - desired_aspect) < 0.01:
                    video_url = vf['link']
                    break
            if not video_url:
                continue  # Skip if no matching video is found
            file_extension = os.path.splitext(video_url)[1].split('?')[0] or '.mp4'
            file_name = os.path.join(dir_path, f"{item['id']}{file_extension}")
            download_success = download_file(video_url, file_name)
            file_url = video_url

        if download_success:
            # Collect metadata
            metadata = {
                'file_name': file_name,
                'file_url': file_url,
                'website': website,
                'keywords': keyword_set,
                'categories': args['categories'],
                'styles': args['styles'],
                'content_type': content_type,
                'quality': quality,
                'format': fmt,
                'id': item['id'],
                'original_url': item['url']
            }
            metadata_list.append(metadata)
            downloaded_count += 1
            print(f"Downloaded {file_name}")
        else:
            logging.info(f"Failed to download {file_name}")

    if not metadata_list:
        logging.info(f"No valid items found to save for query: {keyword_set}")
        return

    # Save metadata to JSON file
    metadata_file = os.path.join(metadata_path, f"{website}_{keyword_dir}_{categories}_{styles}_{content_type}_{quality}_{fmt_sanitized}.json")
    os.makedirs(metadata_path, exist_ok=True)
    with open(metadata_file, 'a') as f:
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
                return True
            else:
                logging.error(f"Failed to download {url}: Status code {response.status_code}")
                return False
        else:
            logging.info(f"File already exists: {file_name}")
            return True
    except Exception as e:
        logging.error(f"Failed to download {url}: {e}")
        return False
