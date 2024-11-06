# setup.py
import os
import json
import subprocess
import sys

def install_dependencies():
    print("Installing required packages...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])

def create_directories(db_path):
    dirs = [
        "scrapers",
        "logs",
        "docs",
        "crash_reports",
        "metadata"  # New directory for metadata files
    ]
    for dir in dirs:
        os.makedirs(dir, exist_ok=True)
    print("\nDirectories created.")

    # Create the database directory at the specified path
    os.makedirs(db_path, exist_ok=True)
    print(f"Database directory created at: {db_path}")

def create_files():
    # Create requirements.txt
    requirements = """requests
    """
    with open("requirements.txt", "w") as f:
        f.write(requirements.strip())

    # Create __init__.py in scrapers directory
    with open(os.path.join("scrapers", "__init__.py"), "w") as f:
        f.write("# Scrapers package")

    # Create scraper.py
    scraper_py_content = '''# scraper.py
import json
import logging
import os
from scrapers import (
    pexels_scraper,
    pixabay_scraper,
    # Add other scraper modules here
)

def load_config():
    with open("config.json") as f:
        return json.load(f)

def setup_logging(log_level):
    logging.basicConfig(
        level=getattr(logging, log_level),
        filename=os.path.join('logs', 'scraper.log'),
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

def get_user_input():
    print("\\nSelect websites to scrape:")
    website_options = {
        '1': 'pexels',
        '2': 'pixabay',
        '3': 'unsplash',
        '4': 'videvo',
        '5': 'mixkit',
        '6': 'opengameart',
        '7': 'vidlery',
        '8': 'nasa'
    }
    for key, value in website_options.items():
        print(f"{key}: {value.capitalize()}")
    websites = input("Enter website numbers separated by space (e.g., 1 2 3): ").split()

    print("\\nSelect content type:")
    print("1: Images")
    print("2: Videos")
    content_type = input("Enter 1 or 2: ")

    print("\\nSelect categories (you can select multiple):")
    category_options = {
        '1': 'AI Generated',
        '2': 'Illustrations',
        '3': 'Anime',
        '4': 'Comics',
        '5': 'Animations',
        '6': 'Infographics',
        '7': 'Realistic',
        '8': 'Real',
        '9': 'Nature',
        '10': 'Technology',
        '11': 'Sports',
        '12': 'Travel',
        '13': 'Fashion',
        '14': 'Food',
        '15': 'Animals',
        '16': 'Architecture',
        '17': 'People',
        '18': 'Business',
        '19': 'Education',
        '20': 'Health'
    }
    for key, value in category_options.items():
        print(f"{key}: {value}")
    categories_input = input("Enter category numbers separated by space (e.g., 1 2 3): ").split()
    categories = [category_options[num] for num in categories_input if num in category_options]

    print("\\nSelect quality:")
    qualities = ['HD', 'UHD', '4K', '1080P']
    for idx, quality in enumerate(qualities, 1):
        print(f"{idx}: {quality}")
    quality_choice = input(f"Enter number (1-{len(qualities)}): ")
    quality = qualities[int(quality_choice)-1]

    print("\\nSelect format:")
    formats = ['16:9', '9:16']
    for idx, fmt in enumerate(formats, 1):
        print(f"{idx}: {fmt}")
    format_choice = input(f"Enter number (1-{len(formats)}): ")
    fmt = formats[int(format_choice)-1]

    # Replace ':' with '-' in format to avoid issues with file paths
    fmt_sanitized = fmt.replace(':', '-')

    keywords = input("\\nEnter keywords for search (separated by commas): ").split(',')
    keywords = [kw.strip() for kw in keywords]

    args = {
        'websites': websites,
        'content_type': content_type,
        'categories': categories,
        'quality': quality,
        'format': fmt,
        'format_sanitized': fmt_sanitized,
        'keywords': keywords
    }
    return args, website_options

def main():
    config = load_config()
    setup_logging(config['log_level'])

    args, website_options = get_user_input()

    selected_websites = [website_options[num] for num in args['websites'] if num in website_options]

    for site in selected_websites:
        try:
            if site == 'pexels':
                pexels_scraper.scrape(args, config)
            elif site == 'pixabay':
                pixabay_scraper.scrape(args, config)
            # Add other scrapers here
            else:
                logging.warning(f"No scraper available for {site}")
        except Exception as e:
            logging.exception(f"An error occurred while scraping {site}")
            with open(os.path.join('crash_reports', f'{site}_crash_report.txt'), 'w') as f:
                f.write(str(e))
            print(f"An error occurred while scraping {site}. Check crash reports.")

if __name__ == "__main__":
    main()
'''
    with open("scraper.py", "w") as f:
        f.write(scraper_py_content)

    # Create scraper modules
    os.makedirs("scrapers", exist_ok=True)

    pexels_scraper_content = '''# scrapers/pexels_scraper.py
import requests
import os
import logging
import json

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
    url = f"https://api.pexels.com/v1/{content_type}/search?query={query}&per_page=15"

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        logging.error(f"Failed to fetch data from Pexels: {response.status_code}")
        return

    data = response.json()
    save_content(data, args, config, 'pexels', content_type)

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

        # Collect metadata
        metadata = {
            'file_name': file_name,
            'file_url': image_url if content_type == 'photos' else video_url,
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
    with open(metadata_file, 'w') as f:
        json.dump(metadata_list, f, indent=4)
    logging.info(f"Metadata saved to {metadata_file}")

def download_file(url, file_name):
    try:
        response = requests.get(url, stream=True)
        with open(file_name, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        logging.info(f"Downloaded {file_name}")
    except Exception as e:
        logging.error(f"Failed to download {url}: {e}")
'''

    with open(os.path.join("scrapers", "pexels_scraper.py"), "w") as f:
        f.write(pexels_scraper_content)

    pixabay_scraper_content = '''# scrapers/pixabay_scraper.py
import requests
import os
import logging
import json

def scrape(args, config):
    api_key = config['api_keys']['pixabay']
    if not api_key:
        logging.error("Pixabay API key is missing.")
        return

    keywords = '+'.join(args['keywords'])
    # Pixabay supports specific categories
    allowed_categories = ['fashion', 'nature', 'backgrounds', 'science', 'education', 'people', 'feelings',
                          'religion', 'health', 'places', 'animals', 'industry', 'food', 'computer', 'sports',
                          'transportation', 'travel', 'buildings', 'business', 'music']
    categories_filtered = [cat.lower() for cat in args['categories'] if cat.lower() in allowed_categories]
    categories = ','.join(categories_filtered)
    query = f"{keywords}"  # Categories are specified separately
    content_type = 'photo' if args['content_type'] == '1' else 'video'

    if content_type == 'photo':
        url = f"https://pixabay.com/api/?key={api_key}&q={query}&image_type=photo"
        if categories:
            url += f"&category={categories}"
    else:
        url = f"https://pixabay.com/api/videos/?key={api_key}&q={query}"
        if categories:
            url += f"&category={categories}"

    response = requests.get(url)
    if response.status_code != 200:
        logging.error(f"Failed to fetch data from Pixabay: {response.status_code}")
        return

    data = response.json()
    save_content(data, args, config, 'pixabay', content_type)

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
        if content_type == 'photo':
            image_url = item['largeImageURL']
            file_name = os.path.join(dir_path, f"{item['id']}.jpg")
            download_file(image_url, file_name)
        else:
            # Select video with desired quality
            videos = item['videos']
            video_url = None
            quality_key = quality.lower()
            if quality_key in videos:
                video_url = videos[quality_key]['url']
            else:
                # Fallback to the highest quality available
                quality_levels = ['large', 'medium', 'small', 'tiny']
                for ql in quality_levels:
                    if ql in videos:
                        video_url = videos[ql]['url']
                        break
            if not video_url:
                continue  # Skip if no video URL is found
            file_name = os.path.join(dir_path, f"{item['id']}.mp4")
            download_file(video_url, file_name)

        # Collect metadata
        metadata = {
            'file_name': file_name,
            'file_url': image_url if content_type == 'photo' else video_url,
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

    # Save metadata to JSON file
    metadata_file = os.path.join(metadata_path, f"{website}_{keywords}_{categories}_{content_type}_{quality}_{fmt_sanitized}.json")
    os.makedirs(metadata_path, exist_ok=True)
    with open(metadata_file, 'w') as f:
        json.dump(metadata_list, f, indent=4)
    logging.info(f"Metadata saved to {metadata_file}")

def download_file(url, file_name):
    try:
        response = requests.get(url, stream=True)
        with open(file_name, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        logging.info(f"Downloaded {file_name}")
    except Exception as e:
        logging.error(f"Failed to download {url}: {e}")
'''

    with open(os.path.join("scrapers", "pixabay_scraper.py"), "w") as f:
        f.write(pixabay_scraper_content)

    # Create docs/tutorial.md
    os.makedirs("docs", exist_ok=True)
    tutorial = """# Scraper Tool Tutorial

## How to Use

1. Run the scraper:
   ```
   python scraper.py
   ```
2. Follow the prompts in the CLI to select options.
3. The scraped content will be saved in the database directory you specified.
4. Metadata files are generated in the 'metadata' directory.

## Available Options

- **Websites**: Choose from the list of supported websites.
- **Content Type**: Images or Videos.
- **Categories**: Select one or more categories from the provided list.
- **Quality**: Select desired quality (e.g., HD, 4K).
- **Format**: Choose aspect ratio (e.g., 16:9, 9:16).
- **Keywords**: Enter search keywords separated by commas.
"""
    with open(os.path.join("docs", "tutorial.md"), "w") as f:
        f.write(tutorial.strip())

    # Create docs/documentation.md
    documentation = """# Scraper Tool Documentation

## Overview

This tool allows you to scrape images and videos from various websites using their APIs. It organizes the downloaded content into a structured database for easy access.

## Modules

- **setup.py**: Initializes the tool.
- **scraper.py**: Main script to run the scraper.
- **scrapers/**: Contains individual scraper modules for each website.

## Configuration

The `config.json` file stores your settings, including API keys and database path.

## Logging

Logs are stored in the `logs/` directory.

## Crash Reports

Any crashes are logged in the `crash_reports/` directory.

## Metadata

Metadata files are stored in the `metadata` directory as JSON files. They include details like file paths, keywords, categories, content type, quality, format, and other relevant metadata.
"""
    with open(os.path.join("docs", "documentation.md"), "w") as f:
        f.write(documentation.strip())

    print("\nFiles created.")

def get_api_keys():
    print("\nPlease enter your API keys (leave blank if not applicable):")
    api_keys = {}
    websites = ["pexels", "pixabay", "unsplash", "videvo", "mixkit", "opengameart", "vidlery", "nasa"]
    for site in websites:
        key = input(f"{site.capitalize()} API Key: ")
        api_keys[site] = key.strip()
    return api_keys

def create_config(db_path, api_keys):
    config = {
        "database_path": db_path,
        "api_keys": api_keys,
        "log_level": "INFO",
        "metadata_path": "metadata"  # Path for metadata files
    }
    with open("config.json", "w") as f:
        json.dump(config, f, indent=4)
    print("\nConfiguration file 'config.json' created.")

def main():
    print("Welcome to the Scraper Tool Setup\n")
    db_path = input("Enter the path where you want the database to be stored: ").strip()
    if not db_path:
        print("Database path is required.")
        return

    create_directories(db_path)
    create_files()
    api_keys = get_api_keys()
    create_config(db_path, api_keys)
    install_dependencies()

    print("\nSetup is complete. You can now run 'python scraper.py' to start scraping.")

if __name__ == "__main__":
    main()