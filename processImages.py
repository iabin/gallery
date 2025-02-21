import os
import uuid
import random
from PIL import Image
from jinja2 import Environment, FileSystemLoader

def process_images():
    """
    1. Looks into the 'images' folder for subfolders (excluding 'generated').
    2. For each found image:
       - Creates a 'full' version (original size, compressed, metadata-free).
       - Creates a 'thumbnail' version (preserves aspect ratio, random fixed width).
       - Generates random UUID filenames and stores them in 'images/generated/<folder>/full'
         and 'images/generated/<folder>/thumbnail'.
    """
    # Directory where this script is located
    base_dir = os.path.dirname(os.path.abspath(__file__))
    images_dir = os.path.join(base_dir, "images")
    generated_dir = os.path.join(images_dir, "generated")

    # Ensure 'generated' exists
    if not os.path.exists(generated_dir):
        os.mkdir(generated_dir)

    # Possible widths for thumbnails
    thumbnail_widths = [250]

    # Iterate over subfolders in 'images', ignoring 'generated'
    for folder in os.listdir(images_dir):
        folder_path = os.path.join(images_dir, folder)
        
        # Ignore if not a directory or if it's 'generated'
        if not os.path.isdir(folder_path) or folder.lower() == "generated":
            continue

        # Prepare target folders in 'generated': <folder>/full and <folder>/thumbnail
        target_folder = os.path.join(generated_dir, folder)
        full_dir = os.path.join(target_folder, "full")
        thumb_dir = os.path.join(target_folder, "thumbnail")
        os.makedirs(full_dir, exist_ok=True)
        os.makedirs(thumb_dir, exist_ok=True)

        # Process images in the current folder
        for filename in os.listdir(folder_path):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                original_path = os.path.join(folder_path, filename)
                try:
                    with Image.open(original_path) as img:
                        # Generate a random name
                        new_name = str(uuid.uuid4())
                        ext = os.path.splitext(filename)[1].lower()
                        new_filename = new_name + ext

                        # 1) 'full' version (same dimensions, compressed, metadata-free)
                        full_output = os.path.join(full_dir, new_filename)
                        if ext in ['.jpg', '.jpeg']:
                            # Convert to RGB to ensure JPEG compatibility
                            img.convert('RGB').save(
                                full_output, 
                                format='JPEG', 
                                quality=100, 
                                optimize=True
                            )
                        else:
                            # PNG
                            img.save(full_output, optimize=True)

                        # 2) 'thumbnail' version (preserves aspect ratio)
                        original_width, original_height = img.size
                        chosen_width = random.choice(thumbnail_widths)
                        calculated_height = int(original_height * chosen_width / original_width)

                        thumb = img.copy().resize((chosen_width, calculated_height), Image.LANCZOS)

                        thumb_output = os.path.join(thumb_dir, new_filename)
                        if ext in ['.jpg', '.jpeg']:
                            thumb.convert('RGB').save(
                                thumb_output, 
                                format='JPEG', 
                                quality=85, 
                                optimize=True
                            )
                        else:
                            thumb.save(thumb_output, optimize=True)

                        print(f"Processed: {original_path} -> {new_filename}")

                except Exception as e:
                    print(f"Error processing {original_path}: {e}")


def generate_gallery_html():
    """
    Iterates through 'images/generated' and builds HTML blocks like:
        <div>
            <h2>Folder</h2>
            <div class="container">
                <div id="animated-thumbnails-gallery-folder">
                    <a href="images/generated/Folder/full/uuid.jpg">
                        <img src="images/generated/Folder/thumbnail/uuid.jpg" />
                    </a>
                    ...
                </div>
            </div>
        </div>

    Also collects the IDs to create a single <script> block that initializes lightGallery.
    Returns:
      - gallery_content: string with all generated <div> blocks
      - gallery_script: the <script> block that initializes all galleries
    """
    base_dir = os.path.dirname(os.path.abspath(__file__))
    generated_dir = os.path.join(base_dir, "images", "generated")

    gallery_blocks = []
    gallery_ids = []

    # Iterate over subfolders in 'generated' (each corresponds to a category/country/etc.)
    for folder in sorted(os.listdir(generated_dir)):
        folder_path = os.path.join(generated_dir, folder)
        if os.path.isdir(folder_path):
            full_dir = os.path.join(folder_path, "full")
            thumb_dir = os.path.join(folder_path, "thumbnail")
            # Check that 'full' and 'thumbnail' subfolders exist
            if not os.path.exists(full_dir) or not os.path.exists(thumb_dir):
                continue

            # Unique ID for this gallery
            gallery_id = f"animated-thumbnails-gallery-{folder.replace(' ', '-').lower()}"
            gallery_ids.append(gallery_id)

            block = []
            block.append("<div>")
            block.append(f'    <h2 class="country-name">{folder}</h2>')
            block.append('    <div class="container">')
            block.append(f'        <div id="{gallery_id}">')

            # For each image in 'thumbnail', create <a> + <img>
            for image_file in sorted(os.listdir(thumb_dir)):
                if image_file.lower().endswith(('.png', '.jpg', '.jpeg')):
                    full_url = f"images/generated/{folder}/full/{image_file}"
                    thumb_url = f"images/generated/{folder}/thumbnail/{image_file}"
                    block.append(f'            <a href="{full_url}">')
                    block.append(f'                <img src="{thumb_url}" />')
                    block.append("            </a>")

            block.append("        </div>")
            block.append("    </div>")
            block.append("</div>")

            gallery_blocks.append("\n".join(block))

    # Join all blocks into one string
    gallery_content = "\n".join(gallery_blocks)

    # Create a single <script> to initialize lightGallery for each ID
    script_lines = []
    script_lines.append("<script>")
    script_lines.append("    const galleryIds = [")
    for idx, gid in enumerate(gallery_ids):
        comma = "," if idx < len(gallery_ids) - 1 else ""
        script_lines.append(f"        '{gid}'{comma}")
    script_lines.append("    ];")
    script_lines.append("    galleryIds.forEach(function(id) {")
    script_lines.append("        lightGallery(document.getElementById(id), {")
    script_lines.append("            thumbnail: true,")
    script_lines.append("        });")
    script_lines.append("    });")
    script_lines.append("</script>")

    gallery_script = "\n".join(script_lines)
    return gallery_content, gallery_script


def generate_full_html():
    """
    Loads the 'template.html' file with Jinja2 and injects:
      - gallery_content: HTML blocks with the galleries
      - gallery_script: <script> block initializing the galleries
    The final result is saved as 'index.html' in the same folder as this script.
    """
    base_dir = os.path.dirname(os.path.abspath(__file__))
    env = Environment(loader=FileSystemLoader(base_dir))
    template = env.get_template('template.html')

    # Get the dynamic content
    gallery_content, gallery_script = generate_gallery_html()

    # Render the template
    rendered_html = template.render(
        gallery_content=gallery_content, 
        gallery_script=gallery_script
    )

    # Save as 'index.html' in the script's directory
    output_file = os.path.join(base_dir, "index.html")
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(rendered_html)

    print(f"Final HTML generated at: {output_file}")


def main():
    """
    Executes:
      1) process_images()    -> Generates compressed images and thumbnails
      2) generate_full_html() -> Creates 'index.html' with the gallery content
    """
    process_images()
    generate_full_html()

if __name__ == "__main__":
    main()
