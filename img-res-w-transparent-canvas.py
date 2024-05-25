from PIL import Image, ImageOps
import os

def resize_images(input_folder, output_folder, canvas_size, quality=85):
    # Ensure output folder exists, create if not
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Loop through all files in input folder
    for filename in os.listdir(input_folder):
        # Check if file is an image
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
            input_path = os.path.join(input_folder, filename)
            output_path = os.path.join(output_folder, filename)

            # Open image file
            img = Image.open(input_path)

            # Calculate the new size maintaining the aspect ratio
            img.thumbnail((canvas_size, canvas_size), Image.Resampling.LANCZOS)

            # Create a new image with a transparent background if the original image has an alpha channel
            if img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info):
                # If the image has an alpha channel or transparency info, create RGBA canvas
                canvas = Image.new('RGBA', (canvas_size, canvas_size), (255, 255, 255, 0))
            else:
                # Otherwise, create RGB canvas
                canvas = Image.new('RGB', (canvas_size, canvas_size), (255, 255, 255))

            # Calculate the position to paste the resized image on the canvas
            paste_position = (
                (canvas_size - img.size[0]) // 2,
                (canvas_size - img.size[1]) // 2
            )

            # Create a mask from the alpha channel of the image
            mask = img.split()[3] if img.mode in ('RGBA', 'LA') else None

            # Paste the resized image onto the canvas
            canvas.paste(img, paste_position, mask)

            # Save the final image as PNG if it has transparency, otherwise save as JPEG
            if canvas.mode == 'RGBA':
                canvas.save(output_path, optimize=True, format='PNG', quality=quality)
            else:
                canvas.save(output_path, optimize=True, format='JPEG', quality=quality)

            print(f"Resized and added padding to {filename} to fit within {canvas_size}x{canvas_size}")

# Define input and output folders
input_folder = 'logo'
output_folder = 'logo_op'

# Define desired canvas size
canvas_size = 200

# Define compression quality (optional, default is 85)
quality = 95

# Resize images
resize_images(input_folder, output_folder, canvas_size, quality)
