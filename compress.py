import os
from PIL import Image

def compress_images_in_folder(folder_path, quality=85):
    """
    Compresses all images in a folder and replaces the originals with the compressed versions.

    Parameters:
        folder_path (str): Path to the folder containing images.
        quality (int): Compression quality (1-100). Higher values mean better quality.
    """
    if not os.path.isdir(folder_path):
        print(f"Error: The folder '{folder_path}' does not exist.")
        return
    
    # Iterate over files in the folder
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        
        # If the file is a directory, recursively call this function
        if os.path.isdir(file_path):
            compress_images_in_folder(file_path, quality)
            continue

        # Skip non-image files
        if not filename.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
            continue
        
        try:
            # Open the image
            with Image.open(file_path) as img:
                # Convert to RGB if necessary (to handle PNGs with transparency)
                if img.mode in ("RGBA", "P"):
                    img = img.convert("RGB")
                
                # Save compressed image to a temporary file
                temp_file_path = file_path + "_temp" + os.path.splitext(filename)[1]  # Add "_temp" before extension
                img.save(temp_file_path, quality=quality, optimize=True)

            # Replace the original file with the compressed version
            os.remove(file_path)
            os.rename(temp_file_path, file_path)

            print(f"Compressed and replaced: {filename}")
        except Exception as e:
            print(f"Error processing file {filename}: {e}")

# Function to scan through the whole Django project directory
def compress_images_in_project(project_dir, quality=85):
    """
    Recursively compress all images in a Django project directory.

    Parameters:
        project_dir (str): Path to the Django project directory.
        quality (int): Compression quality for images.
    """
    if not os.path.isdir(project_dir):
        print(f"Error: The project directory '{project_dir}' does not exist.")
        return

    # Scan the entire project directory, recursively compressing images in subfolders
    compress_images_in_folder(project_dir, quality)

# Usage
project_dir = "./"  # Replace with the path to your Django project
compress_images_in_project(project_dir, quality=85)  # Adjust quality as needed
