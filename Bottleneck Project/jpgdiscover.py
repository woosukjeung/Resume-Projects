import argparse
import os
import logging

logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)

def parse_cmd_arguments():

    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('-p', '--path', type=str, required=True,
                        metavar='', help='Path to iterate over', default=1)
    args = parser.parse_args()
    return args

def list_jpg_files(path):
    output = []
    png_files = []
    for root, dirs, files in os.walk(path):
        dirs.sort()
        files.sort()
        for file in files:
            if '.png' in file:
                full_path = os.path.join(root)
                if full_path not in output:
                    if png_files:
                        output.append(png_files)
                    png_files = []
                    output.append(full_path)
                png_files.append(file)
    output.append(png_files)
    return output

if __name__ == "__main__":
    Argpars = parse_cmd_arguments()
    print(list_jpg_files(Argpars.path))
    Path = '../data/'
    list_jpg_files(Path)
