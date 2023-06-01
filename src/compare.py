import os
import argparse
import matplotlib.pyplot as plt
from skimage import io
from utils import *

def main(ground_truths, colourised, labels, rows, output):
    ground_truth_images = sort_alnum(os.listdir(ground_truths))

    num_images = len(ground_truth_images)
    num_cols = len(colourised) + 1
    if rows is None or rows > num_images:
        rows = num_images

    figsize = (num_cols * 5, rows * 5)

    if (rows != None):
        ground_truth_images = ground_truth_images[:rows]
        colourised = colourised[:rows]

    _, axes = plt.subplots(rows, num_cols, figsize=figsize)
    for i, gt in enumerate(ground_truth_images):
        gt_image = io.imread(os.path.join(ground_truths, gt))

        axes[i, 0].imshow(gt_image)
        axes[i, 0].axis('off')

        for col, colourised_path in enumerate(colourised, start=1):
            colourised_images = sort_alnum(os.listdir(colourised_path))
            col_image = io.imread(os.path.join(colourised_path, colourised_images[i]))

            axes[i, col].imshow(col_image)
            axes[i, col].axis('off')

    # Add labels for each column at the bottom
    for col, label in enumerate(labels):
        axes[-1, col].set_title(label, fontsize=45, y=-0.25)

    plt.tight_layout(pad=5)
    plt.savefig(output)

def get_options() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Plot images side by side for comparison.')
    parser.add_argument('ground_truths', type=str, help='Path to the directory containing the ground truth images')
    parser.add_argument('colourised', type=str, nargs='+', help='Paths to the directories containing the colourised images')
    parser.add_argument('--labels', type=str, nargs='+', help='Labels for each column')
    parser.add_argument('--rows', type=int, default=None, help='Number of rows on the plot')
    parser.add_argument('--output', type=str, default='image_comparison.png', help='Path to save the output plot')
    return parser.parse_args()

if __name__ == '__main__':
    options = get_options()
    main(**vars(options))
