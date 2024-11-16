import os
import time
from datetime import datetime
from pathlib import Path
from PIL import Image
from PIL.ExifTags import TAGS
import re

# 要处理的文件类型，可以按需增加
SUPPORTED_EXTENSIONS = [
    '.jpg', '.jpeg', '.png', '.gif', '.mp4', '.mov', '.avi', '.mkv', '.m4v']


# 格式化时间戳为 YYYYMMDD_HHMMSS
def format_timestamp(timestamp):
    return time.strftime('%Y%m%d_%H%M%S', time.localtime(timestamp))


# 获取文件的创建时间和修改时间，并返回较早的时间
def get_earliest_time(file_path):
    creation_time = os.path.getctime(file_path)  # 获取文件创建时间
    modification_time = os.path.getmtime(file_path)  # 获取文件修改时间
    photo_taken_time = get_photo_taken_time(file_path)  # 如果是照片，获取拍摄时间
    return min(creation_time, modification_time, photo_taken_time)  # 返回较早的时间


def get_photo_taken_time(file_path):
    try:
        # 打开图片文件
        image = Image.open(file_path)

        # 提取 EXIF 数据
        exif_data = image._getexif()

        if exif_data is not None:
            for tag_id, value in exif_data.items():
                tag_name = TAGS.get(tag_id, tag_id)
                if tag_name == "DateTimeOriginal": # 查找拍摄日期字段
                    return datetime.strptime(value, '%Y:%m:%d %H:%M:%S').timestamp()
        return datetime.now().timestamp()
    except Exception as e:
        return datetime.now().timestamp()


# 检查文件是否已经符合重命名格式
def is_already_renamed(filename):
    # 正则匹配 YYYYMMDD_HHMMSS_原文件名.扩展名 的格式
    pattern = r'^\d{8}_\d{6}_.*'
    return re.match(pattern, filename) is not None


# 重命名文件
def rename_files_in_directory(directory):
    # 遍历目标文件夹中的文件
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        file_extension = Path(filename).suffix.lower()

        # 只处理支持的文件类型
        if file_extension in SUPPORTED_EXTENSIONS and os.path.isfile(file_path):
            # 检查是否已经是重命名格式，跳过重命名
            if is_already_renamed(Path(filename).stem):
                print(f"Skipping already renamed file: {filename}")
                continue

            # 获取文件的最早时间
            earliest_time = get_earliest_time(file_path)
            formatted_time = format_timestamp(earliest_time)

            # 获取原始文件名，不包括扩展名
            original_name = Path(filename).stem

            # 构建新的文件名：最早时间_原文件名.扩展名
            new_filename = f"{formatted_time}_{original_name}{file_extension}"
            new_file_path = os.path.join(directory, new_filename)

            # 重命名文件
            os.rename(file_path, new_file_path)
            print(f"Renamed: {filename} -> {new_filename}")


if __name__ == "__main__":
    # 设置要处理的文件夹路径
    target_directory = input("Enter the directory containing the image/video files: ")

    if os.path.isdir(target_directory):
        rename_files_in_directory(target_directory)
        print("All files have been renamed.")
    else:
        print("Invalid directory. Please check the path and try again.")

    input("Press Enter to exit...")
