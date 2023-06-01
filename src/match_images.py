import os
import numpy as np
from PIL import Image, ImageOps
from skimage.metrics import structural_similarity as ssim
import argparse

def rename_matching_files(folder1, folder2):
    folder1_files = [f for f in os.listdir(folder1) if os.path.isfile(os.path.join(folder1, f))]
    folder2_files = [f for f in os.listdir(folder2) if os.path.isfile(os.path.join(folder2, f))]

    for file1 in folder1_files:
        file1_path = os.path.join(folder1, file1)

        if not file1.lower().endswith('.png'):
            continue  # Skip non-PNG files in Folder 1

        # Convert the image to grayscale and equalize the histogram
        image1 = Image.open(file1_path).convert('L')
        image1_eq = ImageOps.equalize(image1)

        for file2 in folder2_files:
            file2_path = os.path.join(folder2, file2)

            if not file2.lower().endswith('.png'):
                continue  # Skip non-PNG files in Folder 2

            # Convert the image in Folder 2 to grayscale and equalize the histogram
            image2 = Image.open(file2_path).convert('L')
            image2_eq = ImageOps.equalize(image2)

            # Calculate the structural similarity index (SSIM) between the images
            similarity = ssim(np.array(image1_eq), np.array(image2_eq))

            # If the similarity is above a certain threshold, rename the file in Folder 2
            if similarity > 0.5:
                new_file2_path = os.path.join(folder2, file1)
                os.rename(file2_path, new_file2_path)
                print(f"Renamed '{file2_path}' to '{new_file2_path}'")
                folder2_files.remove(file2)  # Remove the renamed file from the list
                break  # Move on to the next file in Folder 1

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Rename matching images in Folder 2 to match filenames in Folder 1.')
    parser.add_argument('folder1', type=str, help='Path to Folder 1')
    parser.add_argument('folder2', type=str, help='Path to Folder 2')
    args = parser.parse_args()

    folder1 = args.folder1
    folder2 = args.folder2

    rename_matching_files(folder1, folder2)