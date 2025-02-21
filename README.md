# GALLERY

[SEE THE EXAMPLE SITE](https://iabin.github.io/gallery)

A Python-based tool to automatically **process images** and generate a **LightGallery**-powered HTML gallery.  
It creates **compressed** (metadata-free) full-size images, **thumbnails** with preserved aspect ratio, and an `index.html` file displaying all processed images.

## Table of Contents

1. [Overview](#overview)  
2. [Requirements](#requirements)  
3. [Installation](#installation)  
4. [Project Structure](#project-structure)  
5. [Usage](#usage)  
6. [How It Works](#how-it-works)  
7. [Customization](#customization)  
8. [Troubleshooting](#troubleshooting)  
9. [License](#license)

---

## Overview

This project automates:

1. **Image Processing**:  
   - Removes metadata and compresses images.  
   - Preserves original dimensions for **full** versions.  
   - Creates **thumbnail** versions with a randomly chosen width (to add variety), maintaining the original aspect ratio.  
   - Assigns a **UUID-based filename** to each processed image.

2. **Gallery Generation**:  
   - Uses [Jinja2](https://pypi.org/project/Jinja2/) to inject processed images into an HTML template.  
   - Creates a single **`index.html`** showcasing all processed images via [LightGallery](https://www.lightgalleryjs.com/).  
   - Groups images by subfolder (e.g., `mexico`, `usa`) and initializes a separate LightGallery instance for each group.

---

## Requirements

- **Python 3.7+**  
- [**Pillow**](https://pypi.org/project/Pillow/) (for image manipulation)  
- [**Jinja2**](https://pypi.org/project/Jinja2/) (for templating)  
- [**LightGallery**](https://www.lightgalleryjs.com/) (front-end library to display galleries)

> **Note**: LightGallery files (`lightgallery.min.js`, `lightgallery-bundle.min.css`, etc.) should be placed in a `lib/ligthGallery/` folder, or adjust your paths accordingly in `template.html`.

---

## Installation

1. **Clone or download** this repository.  
2. **Install dependencies** (Pillow, Jinja2) in your environment:

   ```bash
   pip install pillow jinja2
   ```

3. **Ensure LightGallery** is set up in `lib/ligthGallery/`. You can get it from [npm](https://www.npmjs.com/package/lightgallery) or from the [official LightGallery site](https://www.lightgalleryjs.com/).  
4. **Place your images** in subfolders inside the `images/` directory (e.g., `images/mexico/`, `images/usa/`, etc.).

---

## Project Structure

A typical layout looks like this:

```
GALLERY/
├── processImages.py        <-- Main Python script
├── template.html           <-- Jinja2 template for the HTML
├── lib/
│   └── ligthGallery/       <-- LightGallery JS/CSS files
└── images/
    ├── example1/             <-- Example folder with original images
    ├── example2/             <-- Another folder with original images
    └── generated/          <-- Processed images are stored here
```

> **Note**: The `generated/` folder will be created automatically if it doesn’t exist.

---

## Usage

1. **Add your images** into subfolders under `images/` (e.g., `images/mexico`, `images/usa`).  
2. **Run the script**:

   ```bash
   python processImages.py
   ```

   The script will:
   - Process and compress images into `images/generated/<folder>/full` and `images/generated/<folder>/thumbnail`.
   - Generate a new `index.html` in the **same directory** as `processImages.py`.

3. **Open `index.html`** in your browser to view your gallery with LightGallery functionality.

---

## How It Works

1. **`process_images()`**  
   - Iterates through every subfolder in `images/`, skipping `generated/`.  
   - For each image (`.jpg`, `.jpeg`, `.png`), it:
     - Generates a random UUID filename to avoid metadata or naming collisions.
     - Saves a **full** version (original size, compressed, no metadata).  
       - For JPEG, uses `quality=85` and `optimize=True`.
       - For PNG, uses `optimize=True`.
     - Saves a **thumbnail** version with a randomly chosen width `[150, 200, 250, 300]`.  
       - Preserves aspect ratio by computing the new height proportionally.
   - Outputs the processed images to `images/generated/<folder>/full` and `images/generated/<folder>/thumbnail`.

2. **`generate_gallery_html()`**  
   - Looks at `images/generated/` to find subfolders (one per category).  
   - Builds an HTML `<div>` block for each category, containing:
     - A `<h2>` with the folder name (e.g., `mexico`, `usa`).
     - A `<div>` container with an ID (e.g., `animated-thumbnails-gallery-mexico`).
     - `<a>` tags linking to the **full** images, with `<img>` tags for the **thumbnail** versions.
   - Collects these `<div>` blocks into `gallery_content`.
   - Creates a single `<script>` block (`gallery_script`) that calls `lightGallery(...)` for each ID.

3. **`generate_full_html()`**  
   - Loads `template.html` using Jinja2.
   - Injects `gallery_content` and `gallery_script` into the template.  
   - Saves the final output as `index.html`.

4. **`main()`**  
   - Calls `process_images()` first, then `generate_full_html()`.

---

## Customization

- **Thumbnail Widths**:  
  Edit the list `thumbnail_widths = [250]` in `process_images()` to change possible thumbnail widths or add new ones.

- **Compression Quality**:  
  Modify the `quality=85` parameter in `process_images()` for JPEG compression if you need higher or lower quality.

- **Template**:  
  Adjust the `template.html` file to change layout, styling, or script references.  
  - Place your custom CSS/JS in the `<head>` or near the end of `<body>` as needed.

- **Output Path**:  
  The script currently saves `index.html` to the **same directory** as `processImages.py`.  
  Change the `output_file` path in `generate_full_html()` if you want a different location.

---

## Troubleshooting

1. **`ImportError: No module named PIL` or `No module named jinja2`**  
   - Run `pip install pillow jinja2` to install the missing dependencies.

2. **Images Not Found or Not Processed**  
   - Ensure your images have valid extensions (`.jpg`, `.jpeg`, `.png`) and are located in `images/<folder>`.  
   - Verify you’re not storing them in `images/generated/` by mistake.

3. **LightGallery Not Loading**  
   - Check that `lib/ligthGallery/lightgallery.min.js` and `lib/ligthGallery/css/lightgallery-bundle.min.css` exist.  
   - Update paths in `template.html` if you placed LightGallery elsewhere.

4. **No `index.html` Generated**  
   - Confirm the script can find `template.html`.  
   - The template must be in the same directory as `processImages.py` (or update the `FileSystemLoader` path accordingly).

---

## License

This project is released under the [MIT License](https://opensource.org/licenses/MIT). Feel free to modify and distribute it according to your needs.  

