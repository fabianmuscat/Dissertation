from enum import Enum
from serpapi import GoogleSearch

class GoogleImageSearchApi:
    class Tools(Enum):
        class ImageTypes(super):
            PHOTO = "photo"
            CLIP_ART = "clipart"
            FACE = "face"
            LINE = "lineart"
            ANIMATED = "animated"

        class Colours(super):
            FULL = "color"
            BW = "gray"
            TRANSPARENT = "trans"

        class FileTypes(super):
            JPG = "jpg"
            PNG = "png"

        IMAGE_TYPE = "itp"
        COLOUR = "ic"
        FILE_TYPE = "ift"
        PAGE_NO = "ijn"
        RESULTS = "num"

    def __init__(self, api_key: str) -> None:
        self.__valid_tools = [tool.value for tool in self.Tools]
        self.__params = {
            "api_key": api_key,
            "engine": "google",
            "google_domain": "google.com",
            "tbm": "isch",
            "gl": "us",
            "hl": "en",
            "num": 100,
        }

    def __extract_params(self, params: dict) -> str:
        return ",".join(map(lambda tool: f"{tool[0].value}:{tool[1]}", params.items()))

    def search(self, query: str, image_cnt: int, start: int = 0, tools=None) -> list:
        if image_cnt >= 100 and image_cnt % 100 != 0:
            raise ValueError(
                f"Number of images must be divisible by 100. Got {image_cnt}"
            )

        page_no = start
        pages = (image_cnt / 100) + start

        self.__params["q"] = query
        if tools != None:
            self.__params["tbs"] = self.__extract_params(tools)

        images = []

        while page_no < pages and len(images) <= image_cnt:
            self.__params["ijn"] = str(page_no)
            search = GoogleSearch(self.__params)
            results = search.get_dict()

            if "error" in results:  # no images found
                return images

            for image in results["images_results"]:
                original = image["original"]
                if original in images:  # image has already been added so ignoring it
                    continue

                images.append(original)
            page_no += 1

        return images

Tools = GoogleImageSearchApi.Tools
ImageTypes = Tools.ImageTypes
Colours = Tools.Colours
FileTypes = Tools.FileTypes