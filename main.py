import os
from barcode import Code128
from barcode.writer import ImageWriter
from PIL import Image
from datetime import datetime

# Set folder name based on current date and time
current_time = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
ROOT_PATH = f'./barcode_image/{current_time}/'
FILE_PATH_BARCODE = 'barcode_data.txt'
SPACING = 50  # Set spacing between images

def ensure_directory_exists(path: str):
    if not os.path.exists(path):
        os.makedirs(path)
        print(f"Folder {path} created successfully")

def genbarcode(barcode_data: str, no: int) -> str:
    try:
        # Generate barcode in Code 128 format
        barcode_instance = Code128(barcode_data, writer=ImageWriter())
        # Save the barcode image in the specified path
        filename = barcode_instance.save(f'{ROOT_PATH}barcode_{no}')
        print(f"Barcode for {barcode_data} created at {filename}.png")
        return filename
    except Exception as e:
        print(f"Error generating barcode for {barcode_data}: {e}")
        return None

def read_and_generate_barcodes(file_path: str):
    barcode_list = []
    try:
        if not os.path.exists(file_path):
            print(f"File {file_path} not found")
            return barcode_list

        with open(file_path, 'r') as file:
            print(f"Reading file {file_path}")
            for line in file:
                barcode_data = line.strip()
                if barcode_data:
                    barcode_list.append(str(barcode_data))
                    print(f"Added barcode data: {barcode_data}")
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
    return barcode_list

def create_combined_image(image_files: list, output_file: str, width: int, height: int):
    print(f"Creating combined image at {output_file}")
    images = [Image.open(img) for img in image_files]

    # Set size of combined image (adding spacing)
    combined_width = width * 2 + SPACING  # 2 images in one row + spacing
    combined_height = height * 2 + SPACING  # 2 rows + spacing

    # Create new image for combining
    combined_image = Image.new('RGB', (combined_width, combined_height), (255, 255, 255))

    # Paste barcode images into the combined image
    for index, image in enumerate(images):
        x = (index % 2) * (width + SPACING)
        y = (index // 2) * (height + SPACING)
        combined_image.paste(image, (x, y))
        print(f"Pasted image at position {(x, y)}")

    combined_image.save(output_file)
    print(f"Combined image saved at {output_file}")

    # Close all images after combining
    for image in images:
        image.close()

def delete_files(files: list):
    for file_path in files:
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                print(f"File {file_path} deleted successfully")
            except Exception as e:
                print(f"Error deleting file {file_path}: {e}")

if __name__ == "__main__":
    print("Program started")
    ensure_directory_exists(ROOT_PATH)

    barcode_data_list = read_and_generate_barcodes(FILE_PATH_BARCODE)
    if not barcode_data_list:
        print("No barcode data found in file or unable to read file")
    else:
        num = 1
        image_files = []
        created_files = []

        for code in barcode_data_list:
            filename = genbarcode(barcode_data=code, no=num)
            if filename:
                print(f"Barcode for {code} saved as file: {filename}.png")
                image_files.append(filename)
                created_files.append(filename)
            num += 1

        if image_files:
            first_image = Image.open(image_files[0])
            width, height = first_image.size
            first_image.close()

            batch_number = 1
            for i in range(0, len(image_files), 4):
                batch_files = image_files[i:i + 4]
                if len(batch_files) < 4:
                    for j in range(4 - len(batch_files)):
                        blank_image = Image.new('RGB', (width, height), (255, 255, 255))
                        blank_image_path = f'{ROOT_PATH}blank_{batch_number}_{j}.png'
                        blank_image.save(blank_image_path)
                        batch_files.append(blank_image_path)
                        created_files.append(blank_image_path)
                output_file = f'{ROOT_PATH}combined_barcodes_{batch_number}.png'
                create_combined_image(batch_files, output_file, width, height)
                print(f"Combined barcode image batch {batch_number} saved as: {output_file}")
                batch_number += 1

            delete_files(created_files)
        else:
            print("No barcode data available for creating combined image")
