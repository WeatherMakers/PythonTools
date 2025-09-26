import os
from PIL import Image
import numpy as np

""" 功能：将一个序列分割为多个

:param input_dir: 待处理序列路径
:param output_dirs: 分割后输出路径
:param min_frame: 最小帧号
:param max_frame: 最大帧号
:param crop_regions: 裁剪坐标

"""
def clipTexture(input_dir, output_dirs, min_frame, max_frame, crop_regions):
    # 创建输出文件夹结构
    for dir in output_dirs:
        os.makedirs(dir, exist_ok=True)

    for i in range(min_frame, max_frame + 1):
        # 生成输入文件名（三位数补零）
        file_name = f"frame_{i:03d}.png"
        input_file = input_dir + file_name

        try:
            with Image.open(input_file) as img:
                # 遍历裁剪区域
                for idx, region in enumerate(crop_regions, 0):
                    # 执行裁剪
                    cropped = img.crop(region)

                    # 生成输出路径
                    output_file = os.path.join(output_dirs[idx], file_name)

                    # 保存图片
                    cropped.save(output_file)
                    print(f"已处理: {file_name} -> {output_file}")

        except FileNotFoundError:
            print(f"警告: 文件 {input_file} 不存在，已跳过")
            continue

    print("所有图片处理完成！")

""" 功能：将 4 个序列按标号对齐，作为通道合并为一个序列

:param input_dirs: 待合并序列路径
:param output_dir: 合并后输出路径
:param min_frame: 最小帧号
:param max_frame: 最大帧号

"""
def channel_multiplexing(input_dirs, output_dir, min_frame, max_frame):
    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)

    for frame_num in range(min_frame, max_frame + 1):
        # 生成三位数文件名
        filename = f"frame_{frame_num:03d}.png"

        # 初始化通道字典
        channels = {'R': None, 'G': None, 'B': None, 'A': None}

        try:
            # 读取四个裁剪文件并提取R通道
            for i, channel in enumerate(['R', 'G', 'B', 'A'], 0):
                img_path = os.path.join(input_dirs[i], filename)
                with Image.open(img_path) as img:
                    # 提取R通道（实际使用原图的R通道）
                    channels[channel] = img.split()[0]

            # 合成RGBA图像
            merged = Image.merge('RGBA', (
                channels['R'],
                channels['G'],
                channels['B'],
                channels['A']
            ))

            # 保存结果
            merged.save(os.path.join(output_dir, filename))
            print(f"成功合成：{filename}")

        except Exception as e:
            print(f"处理 {filename} 时出错：{str(e)}")
            continue

    print("所有帧合成完成！")

if __name__ == '__main__':

    input_dir = "snow_asset\\3.moderate_snow(128frames)\\moderate_snow_fore\\"
    output_dirs_prefix = "snow_asset\\clips_from_moderate_snow\\Snow_Fore_clip\\"
    output_dirs = [output_dirs_prefix + 'crop' + str(i) for i in range(1, 5)]
    crop_regions = [
        (0, 0, 736, 414),  # 左上区域
        (736, 0, 1472, 414),  # 右上区域
        (0, 414, 736, 828),  # 左下区域
        (736, 414, 1472, 828)  # 右下区域
    ]
    clipTexture(input_dir, output_dirs, 1, 128, crop_regions)

    input_dirs = output_dirs
    channel_multiplexing(input_dirs, "snow_asset\\Snow_帧复用\\Snow_Fore", 1, 128)