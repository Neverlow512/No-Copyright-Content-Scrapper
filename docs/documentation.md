# Scraper Tool Documentation

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