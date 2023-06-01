import os
import shutil
import numpy as np
import argparse
from utils import *

def move_images(source_folders, destination_folder):
    for f in source_folders:
        folder = f.split("/")[-1]
        folder_path = os.path.join(os.getcwd(), f)
        colourised_path = os.path.join(folder_path, 'colourised.png')
        ground_truth_path = os.path.join(folder_path, 'ground_truth.png')

        if os.path.exists(colourised_path):
            new_name = f'{folder}_col.png'
            new_path = os.path.join(destination_folder, 'colourised', new_name)
            os.makedirs(os.path.dirname(new_path), exist_ok=True)
            shutil.move(colourised_path, new_path)
            os.remove(colourised_path)

        if os.path.exists(ground_truth_path):
            new_name = f'{folder}.png'
            new_path = os.path.join(destination_folder, 'ground_truths', new_name)
            os.makedirs(os.path.dirname(new_path), exist_ok=True)
            shutil.move(ground_truth_path, new_path)
            os.remove(ground_truth_path)

def main(source_folders, destination_folder):
    move_images(source_folders, destination_folder)
    print("Images moved successfully!")

def get_options() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Move images to destination folders.')
    parser.add_argument('source_folders', type=str, nargs='+', help='Paths to the source folders')
    parser.add_argument('--destination', type=str, default='.', help='Path to the destination folder')
    return parser.parse_args()

if __name__ == '__main__':
    options = get_options()
    main(**vars(options))
