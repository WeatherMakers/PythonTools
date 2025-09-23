import cv2
import numpy as np
from pathlib import Path
#此脚本主要针对闪电等需要进行裁剪的素材，可以将其裁剪至最小，方便压缩图片分辨率，裁剪后可以再搭配ScaleChange.py使用

def cv2_imread_unicode(path):
    """支持中文路径读取 + 保留透明度通道"""
    stream = np.fromfile(str(path), dtype=np.uint8)
    return cv2.imdecode(stream, cv2.IMREAD_UNCHANGED)  # 读取 RGBA
def save_with_unicode(path, image):
    """支持中文路径保存"""
    ext = Path(path).suffix
    cv2.imencode(ext, image)[1].tofile(str(path))

def find_nonblack_bbox(img, threshold):
    """仅对 RGB 部分判断非黑像素，忽略 Alpha"""
    if img.shape[2] == 4:
        rgb = img[..., :3]
    else:
        rgb = img
    mask = np.any(rgb > threshold, axis=2)
    coords = np.argwhere(mask)
    if coords.size == 0:
        return None
    y0, x0 = coords.min(axis=0)
    y1, x1 = coords.max(axis=0) + 1
    return x0, y0, x1 - x0, y1 - y0

def find_nonblack_bbox_with_alpha(img, threshold):
    """判断 RGB > threshold 且 Alpha > 0 的区域，返回最小边界框 (x, y, w, h)"""
    if img.shape[2] < 4:
        # 没有 Alpha 通道时，退回到只判断 RGB
        rgb = img
        mask = np.any(rgb > threshold, axis=2)
    else:
        rgb = img[..., :3]
        alpha = img[..., 3]
        # 非黑区域需满足 RGB 任一通道大于阈值或Alpha通道大于0
        mask = (np.any(rgb > threshold, axis=2)) | (alpha > 0)

    coords = np.argwhere(mask)
    if coords.size == 0:
        return None
    y0, x0 = coords.min(axis=0)
    y1, x1 = coords.max(axis=0) + 1
    return x0, y0, x1 - x0, y1 - y0


def process_lightning_images(input_folders, base_output_root, threshold=10):
    all_image_paths = []
    folder_map = {}

    # 收集所有图像路径并记录它来自哪个文件夹
    for folder in input_folders:
        folder_path = Path(folder)
        if not folder_path.exists():
            print(f"⚠️ 跳过不存在的文件夹: {folder}")
            continue
        for img_path in folder_path.rglob("*"):
            if img_path.suffix.lower() in (".png", ".jpg", ".jpeg", ".bmp", ".tiff"):
                full_path = img_path.resolve()
                all_image_paths.append(full_path)
                folder_map[full_path] = folder_path

    print(f"共找到 {len(all_image_paths)} 张图片")

    # 计算所有图像的统一裁剪区域
    min_x, min_y, max_x, max_y = float('inf'), float('inf'), 0, 0
    for path in all_image_paths:
        img = cv2_imread_unicode(path)
        if img is None:
            print(f"⚠️ 无法读取图像: {path}")
            continue
        bbox = find_nonblack_bbox_with_alpha(img, threshold) #这里如果不要透明度通道 就换函数find_nonblack_bbox
        if bbox is None:
            print(f"⚠️ {path.name} 未检测到非黑区域")
            continue
        x, y, w, h = bbox
        min_x = min(min_x, x)
        min_y = min(min_y, y)
        max_x = max(max_x, x + w)
        max_y = max(max_y, y + h)

    if min_x == float('inf'):
        print("❌ 没有找到有效的非黑区域")
        return

    crop_w, crop_h = max_x - min_x, max_y - min_y
    print(f"统一裁剪区域: x={min_x}, y={min_y}, 宽度={crop_w}, 高度={crop_h}")

    # 对每张图片执行裁剪并保存
    for path in all_image_paths:
        img = cv2_imread_unicode(path)
        if img is None:
            continue

        cropped = img[min_y:max_y, min_x:max_x]
        h, w = cropped.shape[:2]
        channels = cropped.shape[2] if len(cropped.shape) == 3 else 1
        result = np.zeros((crop_h, crop_w, channels), dtype=np.uint8)
        result[:h, :w] = cropped

        origin_folder = folder_map[path]
        output_folder = origin_folder.parent / f"{origin_folder.name}处理后"
        output_folder.mkdir(parents=True, exist_ok=True)

        output_path = output_folder / f"{path.stem}_crop.png"
        save_with_unicode(output_path, result)

    print("✅ 所有图片已完成裁剪并保存到各自对应的文件夹中")


if __name__ == "__main__":
    input_folders = [
        "./5.24/闪电/lightning/lightning0",
        "./5.24/闪电/lightning/lightning1",
        "./5.24/闪电/lightning/lightning2",
        "./5.24/闪电/lightning/lightning3"
    ]
    base_output_root = "./闪电"  # 其实这里可以不用，但保留是为了兼容性
    process_lightning_images(input_folders, base_output_root, threshold=10)
