import os
import argparse
import requests
import io
import sys
from PIL import Image
from tqdm import tqdm
from urllib3.exceptions import InsecureRequestWarning
from api import *
from utils import *

def download_images(to, urls, file_type, limit):
    requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)
    try:
        if not os.path.exists(to):
            os.makedirs(to)

        if len(os.listdir(to)) > 0:
            res = ""
            while res not in ("y", "n"):
                res = input("Directory is not empty. Existing data will be overwritten. Continue? (y/n): ").lower()

            if res == "n":
                return False

        log(Levels.INFO, f"Downloading {len(urls[:limit])} images...")

        success = 0
        fails = 0
        for i, url in enumerate(tqdm(urls[:limit], desc="Images Downloaded")):
            try:
                content = requests.get(url, stream=True, timeout=10, verify=False).content
                file = io.BytesIO(content)
                image = Image.open(file)
                path = f"{to}/{i}.{file_type}"

                with open(path, "wb") as im:
                    image.save(im)

                success += 1
            except IOError:
                fails += 1
                continue

        log(Levels.INFO, f"{success} images downloaded, {fails} failed")
        log(Levels.SUCCESS, f"Images downloaded to {to}")

        return True
    except Exception as e:
        log(Levels.ERROR, f"Download failed: {e}")
        return False

def get_options() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("-q", "--query", required=True, help="Query to search using Google Images API")
    parser.add_argument("-o", "--output", required=True, help="The directory to save images in")
    parser.add_argument("-s", "--start", type=int, default=0, help="Defines the page number for Google Images")
    parser.add_argument("-r", "--results", type=int, default=100, help="Number of images to search (default: 100)")
    return parser.parse_args()

def main(query, output, start, results):
    google = GoogleImageSearchApi(API_KEY)
    tools = {
        Tools.IMAGE_TYPE: ImageTypes.PHOTO,
        Tools.COLOUR: Colours.FULL,
        Tools.FILE_TYPE: FileTypes.JPG,
    }

    images = google.search(query, results, start, tools)
    if len(images) < 1:
        log(Levels.ERROR, "No images found")
        sys.exit(-1)

    download_images(output, images, FileTypes.JPG, results)

if __name__ == "__main__":
    try:
        options = get_options()
        main(**vars(options))
    except Exception as e:
        print(e)
        sys.exit()
