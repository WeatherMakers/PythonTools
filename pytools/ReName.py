import os
import glob
#此脚本主要更改图片的文件名为 fream_00x，所以pr导出素材时可以先随便命名（其他软件也是 只要有顺序即可），再在这里重命名

def rename_images_to_frames(folder_path="."):
    # 标准化目标文件夹路径
    folder_path = os.path.normpath(os.path.abspath(folder_path))

    extensions = ["*.jpg", "*.jpeg", "*.png", "*.webp", "*.bmp", "*.gif"]
    image_files = []

    # 获取文件列表（绝对路径）
    for ext in extensions:
        image_files.extend(glob.glob(os.path.join(folder_path, ext)))

    # 按文件名自然排序
    image_files.sort(
        key=lambda x: [int(c) if c.isdigit() else c for c in os.path.splitext(os.path.basename(x))[0].split('_')])

    # 重命名
    for idx, old_path in enumerate(image_files, start=1):
        ext = os.path.splitext(old_path)[1].lower()
        new_name = f"frame_{idx:03d}{ext}"
        new_path = os.path.join(folder_path, new_name)

        try:
            # 关键修复：确保所有路径为标准化绝对路径
            old_path = os.path.normpath(old_path)
            if not os.path.exists(old_path):
                print(f"Error: File not found - {old_path}")
                continue

            os.rename(old_path, new_path)
            print(f"Renamed: {os.path.basename(old_path)} -> {new_name}")
        except Exception as e:
            print(f"Failed to rename {os.path.basename(old_path)}: {str(e)}")


if __name__ == "__main__":
    target_folder ="./BigRainDrop"    # 改为你的文件夹路径
    rename_images_to_frames(target_folder)