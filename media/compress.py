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

# Usage
folder_path = "restaurants/"  # Replace with the path to your folder
compress_images_in_folder(folder_path, quality=85)  # Adjust quality as needed
