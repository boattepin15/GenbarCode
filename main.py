import os
from barcode import Code128
from barcode.writer import ImageWriter
from PIL import Image
from datetime import datetime

# กำหนดชื่อโฟลเดอร์ตามวันที่และเวลา
current_time = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
ROOT_PATH = f'./barcode_image/{current_time}/'
FILE_PATH_BARCODE = 'barcode_data.txt'
SPACING = 50  # กำหนดความห่างระหว่างภาพ

def ensure_directory_exists(path: str):
    if not os.path.exists(path):
        os.makedirs(path)
        print(f"สร้างโฟลเดอร์ {path} เรียบร้อยแล้ว")

def genbarcode(barcode_data: str, no: int) -> str:
    try:
        # สร้างบาร์โค้ดในรูปแบบ Code 128
        barcode_instance = Code128(barcode_data, writer=ImageWriter())
        # บันทึกเป็นไฟล์รูปภาพในเส้นทางที่กำหนด
        filename = barcode_instance.save(f'{ROOT_PATH}barcode_{no}')
        return filename
    except Exception as e:
        print(f"เกิดข้อผิดพลาดในการสร้างบาร์โค้ดสำหรับ {barcode_data}: {e}")
        return None

def read_and_generate_barcodes(file_path: str):
    barcode_list = []
    try:
        with open(file_path, 'r') as file:
            for line in file:
                barcode_data = line.strip()
                if barcode_data:
                    barcode_list.append(str(barcode_data))
    except Exception as e:
        print(f"เกิดข้อผิดพลาดในการอ่านไฟล์ {file_path}: {e}")
    return barcode_list

def create_combined_image(image_files: list, output_file: str, width: int, height: int):
    images = [Image.open(img) for img in image_files]

    # กำหนดขนาดของภาพรวม (เพิ่มช่องว่างระหว่างภาพ)
    combined_width = width * 2 + SPACING  # 2 รูปในหนึ่งแถว + ความห่าง
    combined_height = height * 2 + SPACING  # 2 แถว + ความห่าง

    # สร้างภาพใหม่สำหรับการรวมภาพ
    combined_image = Image.new('RGB', (combined_width, combined_height), (255, 255, 255))

    # วางภาพบาร์โค้ดลงในภาพรวม
    for index, image in enumerate(images):
        x = (index % 2) * (width + SPACING)
        y = (index // 2) * (height + SPACING)
        combined_image.paste(image, (x, y))

    combined_image.save(output_file)

    # ปิดไฟล์ภาพทั้งหมดหลังการรวม
    for image in images:
        image.close()

def delete_files(files: list):
    for file_path in files:
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                print(f"ไฟล์ {file_path} ถูกลบเรียบร้อยแล้ว")
            except Exception as e:
                print(f"เกิดข้อผิดพลาดในการลบไฟล์ {file_path}: {e}")

if __name__ == "__main__":
    ensure_directory_exists(ROOT_PATH)

    barcode_data_list = read_and_generate_barcodes(FILE_PATH_BARCODE)
    num = 1
    image_files = []
    created_files = []

    if barcode_data_list:
        for code in barcode_data_list:
            filename = genbarcode(barcode_data=code, no=num)
            if filename:
                print(f"บาร์โค้ดสำหรับ {code} ถูกบันทึกเป็นไฟล์: {filename}.png")
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
                print(f"ภาพรวมบาร์โค้ดชุดที่ {batch_number} ถูกบันทึกเป็นไฟล์: {output_file}")
                batch_number += 1

            delete_files(created_files)
        else:
            print("ไม่มีข้อมูลบาร์โค้ดสำหรับการสร้างภาพรวม")
