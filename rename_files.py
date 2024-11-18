import os
import time
from datetime import datetime
from pathlib import Path
from PIL import Image
from PIL.ExifTags import TAGS
import re
import ffmpeg
from dateutil import parser

# 要处理的文件类型，可以按需增加
IMG_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.gif']
VID_EXTENSIONS = ['.mp4', '.mov', '.avi', '.mkv', '.m4v']
SUPPORTED_EXTENSIONS = [*IMG_EXTENSIONS, *VID_EXTENSIONS]

# 格式 YYYYMMDD_HHMMSS_原文件名.扩展名
TARGET_FILENAME = r'^\d{8}[\s]?_[\d{6}_]*.*'

# 格式 YYYY_MM_DD_HH_mm_IMG_编号.扩展名
APPLE_FILENAME = r'^(\d{4})_(\d{2})_(\d{2})_(\d{2})_(\d{2})(_IMG_*.*)'


# 格式化时间戳为 YYYYMMDD_HHMMSS
def format_timestamp(timestamp):
    return time.strftime('%Y%m%d_%H%M%S', time.localtime(timestamp))


# 获取文件的创建时间和修改时间，并返回较早的时间
def get_earliest_time(file_path, file_extension):
    creation_time = os.path.getctime(file_path)  # 获取文件创建时间
    modification_time = os.path.getmtime(file_path)  # 获取文件修改时间

    taken_time = 0
    if file_extension in IMG_EXTENSIONS:
        # 如果是照片，获取拍摄时间
        taken_time = get_photo_taken_time(file_path)
    elif file_extension in VID_EXTENSIONS:
        # 如果是照片，获取录制时间
        taken_time = get_video_taken_time(file_path)

    # 返回其中最早的时间
    return min(creation_time, modification_time, taken_time)


def get_photo_taken_time(file_path):
    try:
        # 打开图片文件
        image = Image.open(file_path)

        # 提取 EXIF 数据
        exif_data = image.getexif()

        if exif_data is not None:
            for tag_id, value in exif_data.items():
                tag_name = TAGS.get(tag_id, tag_id)
                if tag_name == "DateTimeOriginal":  # 查找拍摄日期字段
                    return parser.parse(value).timestamp()
        return datetime.now().timestamp()
    except Exception as e:
        return None


def get_video_taken_time(file_path):
    try:
        # 使用 ffmpeg.probe 获取视频的元数据
        metadata = ffmpeg.probe(file_path)
        # 提取 creation_time 元数据
        taken_time = metadata.get('format', {}).get('tags', {}).get('com.apple.quicktime.creationdate', None)
        if taken_time is None:
            # 兼容 Apple 早期版本的元数据格式
            taken_time = metadata.get('format', {}).get('tags', {}).get('date', None)
        if taken_time is None:
            return datetime.now().timestamp()
        return parser.parse(taken_time).timestamp()

    except ffmpeg.Error as e:
        print(f"ffmpeg 错误: {e}")
        return None
    except Exception as e:
        print(f"其他错误: {e}")
        return None


# 检查文件是否已经符合重命名格式
def is_already_renamed(filename):
    return re.match(TARGET_FILENAME, filename) is not None


# 检查文件是否是老版 Apple 照片导出命名格式
def is_apple_namestyle(filename):
    return re.match(APPLE_FILENAME, filename) is not None


def rename_files_in_directory(directory):
    # 遍历目标文件夹中的文件
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        file_extension = Path(filename).suffix.lower()

        # 只处理支持的文件类型
        if file_extension in SUPPORTED_EXTENSIONS and os.path.isfile(file_path):
            # 获取原始文件名，不包括扩展名
            original_name = Path(filename).stem

            # 检查是否已经是重命名格式，跳过重命名
            if is_already_renamed(original_name):
                print(f"Skipping already renamed file: {filename}")
                continue

            if is_apple_namestyle(original_name):
                # 检查是否是 Apple 早期版本的文件名格式
                pattern = APPLE_FILENAME
                new_filename = re.sub(pattern, r"\1\2\3_\4\5\6", f"{original_name}{file_extension}")
            else:
                # 获取文件的最早时间
                earliest_time = get_earliest_time(file_path, file_extension)
                formatted_time = format_timestamp(earliest_time)
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
