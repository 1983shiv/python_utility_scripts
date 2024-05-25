from PIL import Image, ImageOps
import os

def get_dominant_color(image):
    """
    Get the dominant color from the corners of the image.
    """
    # Check if the image is in grayscale
    if image.mode in ('L', '1'):
        # For grayscale images, just take the corner pixel value
        corners = [
            image.getpixel((0, 0)),
            image.getpixel((image.width - 1, 0)),
            image.getpixel((0, image.height - 1)),
            image.getpixel((image.width - 1, image.height - 1))
        ]
        # Average the grayscale values
        avg_color = sum(corners) // len(corners)
        return (avg_color, avg_color, avg_color)
    else:
        # For color images, take the RGB values of the corners
        corners = [
            image.getpixel((0, 0)),
            image.getpixel((image.width - 1, 0)),
            image.getpixel((0, image.height - 1)),
            image.getpixel((image.width - 1, image.height - 1))
        ]
        # Calculate the average color
        avg_color = tuple(
            sum(color[i] for color in corners) // len(corners) for i in range(3)
        )
        return avg_color

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

            # Get the dominant background color from the original image
            bg_color = get_dominant_color(img)

            # Create a new image with the same background color
            canvas = Image.new('RGB', (canvas_size, canvas_size), bg_color)

            # Calculate the position to paste the resized image on the canvas
            paste_position = (
                (canvas_size - img.size[0]) // 2,
                (canvas_size - img.size[1]) // 2
            )

            # Paste the resized image onto the canvas
            canvas.paste(img, paste_position)

            # Save the final image
            canvas.save(output_path, optimize=True, quality=quality)

            print(f"Resized and added padding to {filename} to fit within {canvas_size}x{canvas_size}")

# Define input and output folders
input_folder = 'logo'
output_folder = 'logo_op'

# Define desired canvas size
canvas_size = 200

# Define compression quality (optional, default is 85)
quality = 99

# Resize images
resize_images(input_folder, output_folder, canvas_size, quality)
