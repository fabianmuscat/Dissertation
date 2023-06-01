from PIL import Image, ImageOps
import os
import argparse
import re
import sys
from tqdm import tqdm

class DIR(Enum):
    COLOUR = 1
    GRAY = 2

def sort_alnum(data):
    def alphanum_key(key):
        return [int(c) if c.isdigit() else c.lower() for c in re.split("([0-9]+)", key)]

    return sorted(data, key=alphanum_key)


def convert_to_grayscale(image: Image.Image):
    return ImageOps.grayscale(image)


def make_dirs(directory: DIR):
    os.makedirs(directory.name, exist_ok=True)


def resize_img(image: Image.Image, new_width: int) -> Image.Image:
    ratio: float = image.height / image.width
    new_height = int(new_width * ratio)

    return image.resize((new_width, new_height))


def get_options() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--directory", required=True, help="directory containing images")
    parser.add_argument("-r", "--remove_old", action="store_true", help="removes old images after copying")
    parser.add_argument("-g", "--gray_only", action="store_true", help="creates a directory for grayscale images only")
    parser.add_argument("-rs", "--resize", type=int, help="resize images to the provided value")
    return parser.parse_args()


def main(directory: str, remove_old: bool, gray_only: bool, resize: int) -> bool:
    if not os.path.exists(directory):
        raise IOError(f"Provided directory does not exist: {directory}")

    to_remove = os.path.join(directory, ".DS_Store")
    if os.path.exists(to_remove):
        os.remove(to_remove)

    # Check if any directories are present in the provided directory
    dirs = [
        file
        for file in os.listdir(directory)
        if os.path.isdir(os.path.join(directory, file))
    ]

    if len(dirs) > 0:
        raise IOError(
            f"Files in {os.path.relpath(directory)} must be images. {len(dirs)} directories found."
        )

    # Check if all files are images
    invalid_exts = [
        file
        for file in os.listdir(directory)
        if os.path.splitext(file)[1].lower() not in (".jpg", ".jpeg", ".png")
    ]
    if len(invalid_exts) > 0:
        raise IOError(f"Files must be images. Found {invalid_exts}")

    files = sort_alnum(os.listdir(directory))

    def copy_images(to: DIR, images: list):
        to_dir = os.path.join(directory, to.name)
        os.makedirs(to_dir, exist_ok=True)

        for i, file in enumerate(tqdm(images, desc=f"{to.name} Images")):
            _, ext = os.path.splitext(file)  # split extension from filename
            src = os.path.join(directory, file)
            dst = os.path.join(to_dir, f"{i+1}{ext}")

            img = Image.open(src)
            if img.mode != "RGB":
                img = img.convert(mode="RGB")

            yield dst, resize_img(img, resize) if resize is not None else img

    if not gray_only:
        for dst, image in copy_images(DIR.COLOUR, files):
            image.save(dst)

    gray_images = copy_images(DIR.GRAY, files)
    for dst, image in gray_images:
        gray = convert_to_grayscale(image)
        gray.save(dst)

    if remove_old:
        for file in files:
            os.remove(os.path.join(directory, file))

    return True


if __name__ == "__main__":
    try:
        options = get_options()
        main(**vars(options))
    except Exception as e:
        print(e)
        sys.exit()