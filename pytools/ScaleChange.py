import os
from PIL import Image
#此脚本用于将图片进行等比例缩放，主要用于处理闪电和闪电遮罩这种小素材 不需要高清分辨率的内容
#如果需要改变整个图片的分辨率，不想让它变糊（python改分辨率好像会变糊），建议采用ffmpeg工具

# 支持的图像扩展名
VALID_EXTENSIONS = [".png", ".jpg", ".jpeg", ".bmp", ".webp"]

def compress_image(img: Image.Image, scale: float) -> Image.Image:
    """按指定比例压缩图像，返回压缩后图像和新尺寸"""
    w, h = img.size
    new_size = (int(w * scale), int(h * scale))
    return img.resize(new_size, Image.LANCZOS), new_size

def process_folder(input_folder: str, output_root: str, scales: list[float]) -> None:
    """处理文件夹：按每个比例生成对应分辨率子文件夹，保存同名文件"""
    os.makedirs(output_root, exist_ok=True)

    for filename in os.listdir(input_folder):
        name, ext = os.path.splitext(filename)
        if ext.lower() not in VALID_EXTENSIONS:
            continue

        input_path = os.path.join(input_folder, filename)
        try:
            img = Image.open(input_path)

            for scale in scales:
                img_resized, (nw, nh) = compress_image(img, scale)
                # 子文件夹名如 "512x384"
                subdir = f"{nw}x{nh}"
                out_dir = os.path.join(output_root, subdir)
                os.makedirs(out_dir, exist_ok=True)

                # 保留原文件名
                output_path = os.path.join(out_dir, filename)
                img_resized.save(output_path)
                print(f"✅ 保存: {subdir}/{filename}")

        except Exception as e:
            print(f"⚠️ 处理 {filename} 时出错：{e}")

def main():
    input_folder = "./5.24/闪电/处理后/lightning3处理后"                      # 输入文件夹
    output_folder = "./5.24/闪电/处理后/lightning3处理后"                    # 输出文件夹
   # scales = [1.0,0.9,0.8,0.7,0.6, 0.5, 0.25,0.15,0.05,0.01]                   # 缩放比例列表
    scales = [0.8]                   # 缩放比例列表

    print("🚀 开始处理图像...")
    process_folder(input_folder, output_folder, scales)
    print("✅ 所有图像处理完成。")

if __name__ == "__main__":
    main()
