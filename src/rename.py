import os
import argparse
import sys

VALID_FILE_TYPES = ('jpg', 'jpeg', 'png')

def get_files(path: str) -> list:
    files = []
    for root, _, filenames in os.walk(path):
        for filename in filenames:
            if filename.lower().endswith(VALID_FILE_TYPES):
                file_path = os.path.join(root, filename)
                files.append(file_path)
    files.sort()
    return files

def rename_files(files: list, start_from: int = 0) -> None:
    for idx, file_path in enumerate(files):
        file_dir, file_name = os.path.split(file_path)
        file_name, file_ext = os.path.splitext(file_name)
        new_name = f'{idx + start_from}{file_ext}'
        new_path = os.path.join(file_dir, new_name)
        os.rename(file_path, new_path)

def get_options() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument('dir', type=str, help='Directory containing files to rename')
    parser.add_argument('--start', type=int, default=0, help='Specifies the start index which will be suffixed to the filename')
    return parser.parse_args()

def main(dir: str, start: int) -> None:
    if not os.path.isdir(dir):
        raise OSError("Invalid Directory", "Provided directory does not exist or is not a directory")

    files = get_files(dir)
    rename_files(files, start)
    print('Files renamed successfully')

if __name__ == '__main__':
    try:
        options = get_options()
        main(**vars(options))
    except Exception as e:
        print(e)
        sys.exit()