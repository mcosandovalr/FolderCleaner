import glob
import json
import os
import re
import shutil
import sys
from datetime import datetime
from os.path import split
from pathlib import Path
from PIL import Image, ExifTags
from PIL.ExifTags import TAGS


def check_folder(path: Path):
    try:
        if not os.path.exists(path):
            print(f"creating folder {path}")
            os.mkdir(path)
        else:
            print(f"folder already exists")
    except FileExistsError as error:
        print(f"An exception occurred: {error}")
    except:
        print(f"Unexpected error: {sys.exc_info()[0]}")


def break_date(date_string: str, folder_path):
    year = date_string[:4]
    month = date_string[4:6]
    day = date_string[6:8]
    print(f"Year: {year}, Month: {month}, Day: {day}")
    print("\n")

    month_folder = cal_dic(month, year, folder_path)

    return month_folder


def cal_dic(month_number: str, year: str, folder_path: str):
    month_names = {'01': 'Ene', '02': 'Feb', '03': 'Mar', '04': 'Abr', '05': 'May', '06': 'Jun',
                   '07': 'Jul', '08': 'Ago', '09': 'Sep', '10': 'Oct', '11': 'Nov', '12': 'Dic'}

    month = month_names[month_number]
    return Path(f"{folder_path}/{month} {year}")


def move_file_to_folder(source_path, destination_path, file_name):
    try:
        print(f"moving file")
        shutil.move(Path(f"{source_path}/{file_name}"), Path(f"{destination_path}/{file_name}"))
        print(f"file moved =)")
    except FileExistsError as error:
        print(f"{error}")


def get_date(image_path):
    try:
        with Image.open(image_path) as image:
            exif_data = image.getexif()

            if not exif_data:
                return None

            date_tags = {}

            for tag_id, value in exif_data.items():
                tag_name = ExifTags.TAGS.get(tag_id, tag_id)

                if "date" in tag_name.lower():
                    date_tags[tag_name] = value

            if date_tags:
                print(f"founded {len(date_tags)} tag(s) with the string 'date' in them.")
                if "DateTime" in date_tags:
                    return date_tags["DateTime"]

    except FileNotFoundError:
        print(f"Error: El archivo '{image_path}' no fue encontrado.")
    except OSError:
        print(f"Error: No se pudo abrir el archivo '{image_path}'. Asegúrate de que es una imagen válida.")
    except KeyError:
        print(f"Error: No se encontró la etiqueta 'DateTimeOriginal' en los metadatos EXIF de la imagen.")
    except Exception as e:
        print(f"Error inesperado: {e}")


def process_img_file(file_name, source_path):
    data = re.split(r"[-_]", file_name)
    if len(data) == 5:
        built_date = f"{data[1]}{data[2]}{data[3]}"
    else:
        built_date = data[1]
    path = Path(break_date(built_date, source_path))
    return path


def process_dsc_file(file_name, source_path):
    creation_date = get_date(Path(f"{source_path}\\{file_name}"))
    print(f"Creation date: {creation_date}")
    date_section = str(creation_date).split(" ")
    data = str(date_section[0]).split(":")

    year = data[0]
    month = data[1]

    path = cal_dic(month, year, source_path)
    return path


def process_trashed(file_name, source_path):
    data = file_name.split("_")
    path = Path(break_date(data[1], source_path))
    return path


def read_folder():
    source_path: Path = Path("X:\\Pictures")
    # Define image name patterns
    patterns = [
        r"^IMG-\d{8}-WA\d{4}\.jpg$",
        r"^IMG_\d{8}\.jpg$",
        r"^B\d{3}_?(\d{8})_\d{6}_\d{3}\.jpg$",
        r"^IMG_(\d{4}_\d{2}_\d{2})\.jpg$",
        r"^\.trashed-\d+-IMG_(\d{8})_\d{9}_HDR$"
    ]
    ext = ('.png', '.jpg', '.jpeg','.mp4')
    img_b = ('img','b')
    trashed = '.trashed'
    for file_name in os.listdir(source_path):
        if str(file_name).lower().endswith(ext):
            print(f"{file_name}")
            destination_path = ""
            # revisar si el nombre del archivo comienza con IMG o DSC
            if file_name.lower().startswith(img_b):
                destination_path = process_img_file(file_name, source_path)
            elif file_name.lower().startswith(str('dsc')):
                destination_path = process_dsc_file(file_name, source_path)
            elif file_name.lower().startswith(trashed):
                destination_path = process_trashed(file_name, source_path)
            else:
                continue
            # if destination_path is not None:
            # check if folder exists
            check_folder(destination_path)
            # move the file into the folder
            move_file_to_folder(source_path, destination_path, file_name)

    print("Images moved.   Bye...")


if __name__ == '__main__':
    read_folder()

