import os
import argparse
from utils import *

def main(path):
    csv_data = []

    colourised = sort_alnum(os.listdir(os.path.join(path, 'colourised')))
    ground_truths = sort_alnum(os.listdir(os.path.join(path, 'ground_truths')))

    for i, (gt, col) in enumerate(zip(ground_truths, colourised)):
        stats = get_metrics(os.path.join(path, 'ground_truths', gt), os.path.join(path, 'colourised', col))
        stats['Image'] = i + 1
        csv_data.append(stats)

    write_to_csv(os.path.join(path, 'results.csv'), csv_data)

def get_options() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Process images and generate CSV results.')
    parser.add_argument('path', type=str, help='Path to the directory containing the images')
    return parser.parse_args()

if __name__ == '__main__':
    options = get_options()
    main(**vars(options))
