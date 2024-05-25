from PIL import Image
import os

def resize_images(input_folder, output_folder, width, quality=85):
    # Ensure output folder exists, create if not
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Loop through all files in input folder
    for filename in os.listdir(input_folder):
        # Check if file is an image
        if filename.endswith(('.png', '.jpg', '.jpeg', '.gif')):
            input_path = os.path.join(input_folder, filename)
            output_path = os.path.join(output_folder, filename)

            # Open image file
            img = Image.open(input_path)

            # Calculate proportional height
            ratio = width / float(img.size[0])
            height = int(float(img.size[1]) * ratio)

            # Resize image
            resized_img = img.resize((width, height), Image.Resampling.LANCZOS)

            # Save resized image
            resized_img.save(output_path, optimize=True, quality=quality)

            print(f"Resized {filename} to {width}x{height}")

# Define input and output folders
input_folder = 'logo'
output_folder = 'logo_op_acc2'

# Define desired width
width = 600

# Define compression quality (optional, default is 85)
quality = 99

# Resize images
resize_images(input_folder, output_folder, width, quality)
