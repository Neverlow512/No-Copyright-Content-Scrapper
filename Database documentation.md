# **Documentation: Database Structure and Metadata Handling**

## **1. Overview**

The scraper tool you have developed organizes the downloaded media content (images and videos) into a structured database directory. Alongside the media files, it generates metadata files in JSON format that contain detailed information about each downloaded item. This documentation explains the structure of the database directory and the metadata files, which is essential for building software that can utilize this content for further processing, such as creating videos based on text transcripts.

---

## **2. Database Directory Structure**

The database directory is organized hierarchically to facilitate easy access and management of the media files. The structure is based on several parameters such as the website source, keywords, categories, styles, content type, quality, and format.

### **2.1. Base Directory**

The base directory is specified in your `config.json` file under the key `"database_path"`. This is the root directory where all downloaded media content is stored.

**Example:**

```
"D:\\MediaDatabase"
```

### **2.2. Directory Hierarchy**

The directory hierarchy within the base directory follows this pattern:

```
[base_directory]/
    └── [website]/
        └── [keyword_set]/
            └── [categories]/
                └── [styles]/
                    └── [content_type]/
                        └── [quality]/
                            └── [format]/
                                └── media files
```

**Explanation of Each Level:**

1. **[website]:** The source website from which the media was scraped (e.g., `pexels`, `pixabay`).

2. **[keyword_set]:** The set of keywords used in the search query, with spaces replaced by underscores (e.g., `business_dog`).

3. **[categories]:** The categories selected during the scraping process, concatenated with underscores. If no categories are selected, the folder is named `All`.

4. **[styles]:** The styles selected during the scraping process, concatenated with underscores. If no styles are selected, the folder is named `All`.

5. **[content_type]:** The type of content, either `photos`/`images` or `videos`.

6. **[quality]:** The quality of the media, as selected (e.g., `HD`, `4K`).

7. **[format]:** The aspect ratio of the media, with colons replaced by hyphens (e.g., `16-9`, `9-16`).

### **2.3. Example Directory Path**

Given the following selections:

- Website: `pexels`
- Keywords: `business dog`
- Categories: `Business`, `Animals`
- Styles: `Drawing`, `Cartoon`
- Content Type: `images`
- Quality: `HD`
- Format: `16:9` (stored as `16-9`)

The directory path would be:

```
D:\MediaDatabase\pexels\business_dog\Business_Animals\Drawing_Cartoon\images\HD\16-9\
```

---

## **3. Media Files**

The media files (images or videos) are saved within the final directory in the hierarchy. The filenames are constructed using the unique ID provided by the source website and the appropriate file extension.

**Example:**

- Image file: `1234567.jpg`
- Video file: `7654321.mp4`

---

## **4. Metadata Files**

Metadata is saved in JSON format in a separate directory specified in the `config.json` file under the key `"metadata_path"`. If not specified, it defaults to a directory named `metadata` in the project root.

### **4.1. Metadata Directory**

```
[metadata_path]/
    └── metadata files
```

### **4.2. Metadata File Naming Convention**

The metadata files are named based on the scraping parameters:

```
[website]_[keyword_dir]_[categories]_[styles]_[content_type]_[quality]_[format_sanitized].json
```

**Example:**

```
pexels_business_dog_Business_Animals_Drawing_Cartoon_images_HD_16-9.json
```

### **4.3. Metadata Content Structure**

Each metadata file contains a list of metadata entries, one for each downloaded media file. The structure of each metadata entry is as follows:

```json
{
    "file_name": "Full path to the media file on your local system",
    "file_url": "Original URL of the media file",
    "website": "Source website (e.g., 'pexels')",
    "keywords": "Keywords used in the search query",
    "categories": "Categories selected",
    "styles": "Styles selected",
    "content_type": "Type of content ('photos' or 'videos')",
    "quality": "Quality of the media (e.g., 'HD')",
    "format": "Aspect ratio of the media (e.g., '16:9')",
    "id": "Unique identifier of the media file from the source website",
    "original_url": "Original page URL of the media on the source website"
}
```

**Example Entry:**

```json
{
    "file_name": "D:\\MediaDatabase\\pexels\\business_dog\\Business_Animals\\Drawing_Cartoon\\images\\HD\\16-9\\1234567.jpg",
    "file_url": "https://images.pexels.com/photos/1234567/pexels-photo-1234567.jpeg",
    "website": "pexels",
    "keywords": "business dog",
    "categories": ["Business", "Animals"],
    "styles": ["Drawing", "Cartoon"],
    "content_type": "photos",
    "quality": "HD",
    "format": "16:9",
    "id": "1234567",
    "original_url": "https://www.pexels.com/photo/dog-in-business-suit-1234567/"
}
```

### **4.4. Accessing Metadata**

The metadata files can be parsed using standard JSON parsing libraries in any programming language. By reading these files, you can programmatically access information about the downloaded media files, which is crucial for automating video creation based on text transcripts.

---

## **5. Utilizing the Database and Metadata**

To create software that uses the scraped content, you can follow these steps:

1. **Parse the Metadata Files:**
   - Load the relevant metadata files based on the keywords, categories, styles, content type, quality, and format you need.

2. **Access Media Files:**
   - Use the `file_name` field in the metadata entries to locate and access the media files on your local system.

3. **Filter and Search:**
   - Implement logic to search and filter media files based on specific criteria extracted from your text transcripts.

4. **Integrate with Other Software:**
   - Use the metadata information to integrate the media files into your video creation software, ensuring that the content matches the narrative of your script.