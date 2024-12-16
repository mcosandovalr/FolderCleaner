import os
import shutil
import sys
from pathlib import Path
from PIL import Image
from PIL.ExifTags import TAGS

PICTURES_FOLDER = "X:\\Pictures"

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

            # counter = 1
            for tag_id in exif_data:
                tag_name  = TAGS.get(tag_id, tag_id)
                tag_value = exif_data.get(tag_id)
                # print(f"{counter}.- {tag_id} - {tag_name}: {tag_value}")
                # counter += 1
                if "date" in str(tag_name).lower() or tag_id == 306: # not really sure about using the id
                    return tag_value
    except FileNotFoundError:
        print(f"Error: El archivo '{image_path}' no fue encontrado.")
    except OSError:
        print(f"Error: No se pudo abrir el archivo '{image_path}'. Asegúrate de que es una imagen válida.")
    except KeyError:
        print(f"Error: No se encontró la etiqueta 'DateTimeOriginal' en los metadatos EXIF de la imagen.")
    except Exception as e:
        print(f"Error inesperado: {e}")


def process_img_file(file_name, source_path):
    data = file_name.split("_")

    # TODO: add case for IMG_20240331_002002597_HDR or this thing will break again
    # if len(data) > 3:
    #     return Path(f"{source_path}\\{data[1]} {data[2]}")
    path = Path(break_date(data[1], source_path))
    return path


# this is now useless
def process_dsc_file(file_name, source_path):
    creation_date = get_date(Path(f"{source_path}\\{file_name}"))
    print(f"Creation date: {creation_date}")
    date_section = str(creation_date).split(" ")
    data = str(date_section[0]).split(":")

    year = data[0]
    month = data[1]

    path = cal_dic(month, year, source_path)
    return path


def process_image(file_name, source_path):
    # read EXIF data to get the date
    creation_date = get_date(Path(f"{source_path}\\{file_name}"))
    # if there's no date data get it from the file name
    if not creation_date:
                
        img_b = ('img', 'b')
        # revisar si el nombre del archivo comienza con IMG o DSC (no moar DSC)
        if file_name.lower().startswith(img_b):
            destination_path = process_img_file(file_name, source_path)
        else:
            # leave file in folder for manual review
            return
    print(f"Creation date: {creation_date}")
    date_section = str(creation_date).split(" ")
    data = str(date_section[0]).split(":")

    year = data[0]
    month = data[1]

    path = cal_dic(month, year, source_path)
    return path


def read_folder():
    source_path: Path = Path(PICTURES_FOLDER)
    # files = glob.glob(f"{folder_path}/*.*")
    ext = ('.png', '.jpg', '.mp4')
    for file_name in os.listdir(source_path):
        if str(file_name).lower().endswith(ext):
            print(f"{file_name}")
            destination_path = ""
            destination_path = process_image(file_name, source_path)
            if destination_path is not None:
                # check if folder exists
                check_folder(destination_path)
                # move the file into the folder
                move_file_to_folder(source_path, destination_path, file_name)

    print(" Bye...")


if __name__ == '__main__':
    read_folder()

