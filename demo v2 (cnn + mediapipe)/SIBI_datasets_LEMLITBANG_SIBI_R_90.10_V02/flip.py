from PIL import Image
import os

# Path to the main folder containing images and subfolders
main_folder_path = "E:/Coding stuff/grpPRJ/GP/USTHGroupProject/demo v2 (cnn + mediapipe)/SIBI_datasets_LEMLITBANG_SIBI_R_90.10_V02/SIBI_datasets_LEMLITBANG_SIBI_R_90.10_V02/validation"

# Function to flip images recursively
def flip_images_in_place(folder_path):
    for item in os.listdir(folder_path):
        item_path = os.path.join(folder_path, item)

        # If it's a directory, call the function recursively
        if os.path.isdir(item_path):
            flip_images_in_place(item_path)
        elif item.endswith(".jpg"):
            # Open the image
            img = Image.open(item_path)
            # Flip the image horizontally
            flipped_img = img.transpose(Image.FLIP_LEFT_RIGHT)

            # Generate a new filename with a '_flipped' suffix
            filename, ext = os.path.splitext(item)
            flipped_filename = f"{filename}_flipped{ext}"
            flipped_img_path = os.path.join(folder_path, flipped_filename)

            # Save the flipped image
            flipped_img.save(flipped_img_path)

# Call the function to process all images
flip_images_in_place(main_folder_path)

print("All images have been flipped and saved in the same folders without overwriting.")
