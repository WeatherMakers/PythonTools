import os
import glob
from PIL import Image
import numpy as np
#此文件用于将普通的png图片进行量化四合一操作

def extract_r_channel_with_transparency(image_path):
    """
    提取 R 通道，并将完全透明区域（Alpha=0）的 R 值设为 0
    （半透明区域保留原始 R 值）
    """
    img = Image.open(image_path).convert("RGBA")
    img_array = np.array(img)
    
    # 提取 R 和 Alpha 通道
    r_channel = img_array[:, :, 0].copy()  # R 通道（0~255）
    alpha_channel = img_array[:, :, 3]     # Alpha 通道（0~255）
    
    # 将完全透明区域的 R 值设为 0
    r_channel[alpha_channel == 0] = 0
    
    return Image.fromarray(r_channel, mode="L")

def process_png_to_r_channel(image_path):
    img = Image.open(image_path)
    if img.mode == 'RGBA':
        # 创建黑色背景
        background = Image.new('RGB', img.size, (0, 0, 0))
        background.paste(img, mask=img.split()[3])  # 使用Alpha通道作为掩码
        processed_img = background
    else:
        processed_img = img.convert('RGB')
    return processed_img.split()[0]

def merge_r_channels_to_rgba(r_channels):
    """将4个R通道合并为RGBA图像"""
    if len(r_channels) != 4:
        raise ValueError("需要恰好4个R通道")
    return Image.merge('RGBA', r_channels)

def process_folder(input_dir, output_dir):
    """主处理函数：遍历文件夹，合并通道并保存"""
    os.makedirs(output_dir, exist_ok=True)
    png_files = sorted(glob.glob(os.path.join(input_dir, "*.png")))
    
    # 按每4张一组处理
    for group_idx in range(0, len(png_files), 4):
        group_files = png_files[group_idx:group_idx+4]
        if len(group_files) < 4:
            print(f"跳过最后一组（不足4张）: {len(group_files)} 张")
            break
        
        r_channels = []
        for file_path in group_files:
            r_channel = extract_r_channel_with_transparency(file_path)
            r_channels.append(r_channel)
        
        merged_image = merge_r_channels_to_rgba(r_channels)
        
        output_path = os.path.join(output_dir, f"frame_{group_idx//4 + 1:03d}.png")
        merged_image.save(output_path)
        print(f"已生成: {output_path}")

if __name__ == "__main__":
    input_folder = "./BigRainDroppre"
    output_folder = input_folder + "_mergedpng"
    process_folder(input_folder, output_folder)