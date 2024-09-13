import os, shutil
import sys


def rename(base_path, src_folder, dst_folder, format='png'):
    file_list = os.listdir(base_path + src_folder)
    dst_file_count = len(os.listdir(base_path + dst_folder))
    print(dst_file_count)
    i = 1
    temp_file_name_src = base_path + src_folder + '\\temp'
    temp_file_name_dst = base_path + dst_folder + '\\temp'
    for file_name in file_list:
        if file_name == 'aligned':
            continue
        old_name = base_path + src_folder + '\\' + file_name
        print('oldName: ', old_name)
        os.rename(old_name, temp_file_name_src)
        shutil.move(temp_file_name_src, base_path + dst_folder)
        new_name = base_path + dst_folder + '\\' + str(dst_file_count + i).zfill(5) + '.' + format
        if (os.path.exists(new_name)):
            i += 1
        new_name = base_path + dst_folder + '\\' + str(dst_file_count + i).zfill(5) + '.' + format
        print('newName: ', new_name)
        os.rename(temp_file_name_dst, new_name)
        i += 1


input_str = input("选择图片输出格式（默认jpg）: ")
input_format = 'jpg' if input_str == '' else 'png'
print(format)

basedir = os.path.abspath(os.path.dirname(__file__)) + '\\'
src_folder = 'aligned'
dst_folder = 'aligned_total'

rename(basedir, src_folder, dst_folder, input_format)
