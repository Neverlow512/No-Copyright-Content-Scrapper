# scraper.py
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
    print("\nSelect websites to scrape:")
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

    print("\nSelect content type:")
    print("1: Images")
    print("2: Videos")
    content_type = input("Enter 1 or 2: ")

    print("\nSelect categories (you can select multiple or skip by entering 0):")
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
        '20': 'Health',
        '0': 'Skip category selection'
    }
    for key, value in category_options.items():
        print(f"{key}: {value}")
    categories_input = input("Enter category numbers separated by space (e.g., 1 2 3): ").split()

    if '0' in categories_input or not categories_input:
        categories = []
    else:
        categories = [category_options[num] for num in categories_input if num in category_options and num != '0']

    # Styles Section
    print("\nSelect styles (you can select multiple or skip by entering 0):")
    style_options = {
        '1': 'Drawing',
        '2': 'AI Generated',
        '3': 'Illustrations',
        '4': 'Abstract',
        '5': 'Vintage',
        '6': 'Minimalist',
        '7': 'Surreal',
        '8': 'Pop Art',
        '9': 'Watercolor',
        '10': 'Cartoon',
        '0': 'Skip style selection'
    }
    for key, value in style_options.items():
        print(f"{key}: {value}")
    styles_input = input("Enter style numbers separated by space (e.g., 1 2 3): ").split()

    if '0' in styles_input or not styles_input:
        styles = []
    else:
        styles = [style_options[num] for num in styles_input if num in style_options and num != '0']

    print("\nSelect quality:")
    qualities = ['HD', 'UHD', '4K', '1080P']
    for idx, quality in enumerate(qualities, 1):
        print(f"{idx}: {quality}")
    quality_choice = input(f"Enter number (1-{len(qualities)}): ")
    quality = qualities[int(quality_choice)-1]

    print("\nSelect format:")
    formats = ['16:9', '9:16']
    for idx, fmt in enumerate(formats, 1):
        print(f"{idx}: {fmt}")
    format_choice = input(f"Enter number (1-{len(formats)}): ")
    fmt = formats[int(format_choice)-1]

    # Replace ':' with '-' in format to avoid issues with file paths
    fmt_sanitized = fmt.replace(':', '-')

    keywords_input = input("\nEnter keywords for search (separated by commas): ").split(',')
    # Each keyword set is a trimmed string from the input
    keyword_sets = [kw.strip() for kw in keywords_input if kw.strip()]

    # New prompt for number of results
    num_results = input("\nEnter the number of results you want per keyword (e.g., 50): ")
    try:
        num_results = int(num_results)
    except ValueError:
        print("Invalid number of results. Defaulting to 15.")
        num_results = 15  # Default value

    args = {
        'websites': websites,
        'content_type': content_type,
        'categories': categories,
        'styles': styles,
        'quality': quality,
        'format': fmt,
        'format_sanitized': fmt_sanitized,
        'keyword_sets': keyword_sets,
        'num_results': num_results
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
