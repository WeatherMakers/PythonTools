import os
import cv2
import numpy as np
from PIL import Image, ImageDraw
from loguru import logger
#此脚本用于将序列帧按照x行x列的方式进行合并大图


def compress_images_in_folder(input_folder, output_folder, scale_factor, is_convert_to_white=True):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    for filename in os.listdir(input_folder):
        input_path = os.path.join(input_folder, filename)
        if os.path.isfile(input_path) and filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
            with Image.open(input_path) as img:
                width, height = img.size
                logger.info(f"Compressing {filename}, original size: {width}x{height}")
                new_width = int(width * scale_factor)
                new_height = int(height * scale_factor)
                img_resized = img.resize((new_width, new_height), Image.LANCZOS)

                if is_convert_to_white:
                    if img_resized.mode == 'RGBA':
                        img_resized = img_resized.convert('RGBA')
                        data = img_resized.getdata()
                        new_data = []
                        for item in data:
                            r, g, b, a = item
                            if a > 0:
                                new_data.append((255, 255, 255, a))  # 保持透明度不变，RGB变为白色
                            else:
                                new_data.append(item)  # 保持透明的像素不变
                        img_resized.putdata(new_data)
                    elif img.mode == 'RGB':
                        logger.error(f'Unsupported mode: {img.mode}')
                        return

                output_path = os.path.join(output_folder, filename)
                img_resized.save(output_path, quality=95, optimize=True)
                logger.info(f"Compressed image saved as {output_path}, new size: {new_width}x{new_height}")


def generateSnow(image_folder, save_path='./nearSnow.png'):
    total_images = 128
    images_to_discard = 0
    num_width = 16
    num_height = 8
    images_to_use = []

    discard_indices = set()
    step = total_images / (total_images - images_to_discard)  # 每隔多少张丢弃一张

    for i in range(images_to_discard):
        discard_index = int(i * step)
        discard_indices.add(discard_index)

    all_images = [os.path.join(image_folder, f) for f in os.listdir(image_folder)]

    for i in range(total_images):
        if i not in discard_indices:
            images_to_use.append(all_images[i])

    image_list = [cv2.imread(img_path, cv2.IMREAD_UNCHANGED) for img_path in images_to_use]

    image_height, image_width, channels = image_list[0].shape

    final_image = np.zeros((image_height * num_height, image_width * num_width, channels), dtype=np.uint8)

    for i, img in enumerate(image_list):
        row = i // num_width  # 计算图片所在的行
        col = i % num_width  # 计算图片所在的列
        final_image[row * image_height:(row + 1) * image_height, col * image_width:(col + 1) * image_width] = img
    cv2.imwrite(save_path, final_image)


def generateRain(image_folder, save_path='./nearRain.png', num_width=8, num_height=4):
    total_images = num_width * num_height
    images_to_use = []

    all_images = [os.path.join(image_folder, f) for f in os.listdir(image_folder)]
    logger.info(f'{all_images}')
    for i in range(total_images):
        # if i % 2 == 0:
        #     continue
        images_to_use.append(all_images[i])

    image_list = [cv2.imread(img_path, cv2.IMREAD_UNCHANGED) for img_path in images_to_use]
    image_height, image_width, channels = image_list[0].shape
    final_image = np.zeros((image_height * num_height, image_width * num_width, channels), dtype=np.uint8)

    for i, img in enumerate(image_list):
        # row = num_height - 1 - (i // num_width)  # Calculate row index from bottom
        row = i // num_width  # 计算图片所在的行
        col = i % num_width  # 计算图片所在的列
        final_image[row * image_height:(row + 1) * image_height, col * image_width:(col + 1) * image_width] = img

    cv2.imwrite(save_path, final_image)


def convert_to_alpha(input_image_path, output_image_path, threshold=200):
    img = Image.open(input_image_path).convert('RGB')
    img_array = np.array(img)

    # 创建 Alpha 通道（默认为 0，表示完全透明）
    alpha_channel = np.zeros(img_array.shape[:2], dtype=np.uint8)

    # 使用亮度或颜色阈值来确定哪些区域为闪电（假设亮度较高的地方是闪电）
    # 你可以调整阈值来检测闪电部分
    for i in range(img_array.shape[0]):
        for j in range(img_array.shape[1]):
            r, g, b = img_array[i, j]
            brightness = 0.299 * r + 0.587 * g + 0.114 * b  # 使用亮度公式
            if brightness > threshold:  # 如果亮度大于阈值，表示是闪电区域
                alpha_channel[i, j] = 255  # 设置为完全不透明
            else:
                alpha_channel[i, j] = 0  # 否则完全透明

    # 将 RGB 和生成的 Alpha 通道合并
    img_with_alpha = np.dstack([img_array, alpha_channel])

    # 保存为 PNG 格式，Alpha 通道会被保存
    result_image = Image.fromarray(img_with_alpha)
    result_image.save(output_image_path)


def create_quadrant_image(width, height, colors, save_path="quadrant_image.png"):
    if len(colors) != 4:
        raise ValueError("必须提供四个颜色值，每块区域对应一个颜色。")

    try:
        # 创建一个新的图像，模式为RGB
        image = Image.new("RGB", (width, height), (255, 255, 255))
        draw = ImageDraw.Draw(image)

        half_width = width // 2
        half_height = height // 2

        draw.rectangle([0, 0, half_width, half_height], fill=colors[0])  # 左上
        draw.rectangle([half_width, 0, width, half_height], fill=colors[1])  # 右上
        draw.rectangle([0, half_height, half_width, height], fill=colors[2])  # 左下
        draw.rectangle([half_width, half_height, width, height], fill=colors[3])  # 右下

        image.save(save_path)
        print(f"图片已保存到 {save_path}")
    except Exception as e:
        print(f"保存图片时出错: {e}")


if __name__ == '__main__':
    # input_folder = "./FS24PNG"
    # output_folder = "./FS24PNG_white"
    # scale_factor = 0.5
    # compress_images_in_folder(input_folder, output_folder, scale_factor, is_convert_to_white=True)
    #
    # save_path = './realCloud2_8x16.png'
    # generateRain(input_folder, save_path, num_width = 8, num_height = 16)

    # input_image_path = './Lighting/LT1PNG/frame_06.png'  # 输入的 RGB 图片路径
    # output_image_path = './lighting_alpha.png'  # 输出的 Alpha 图片路径
    # convert_to_alpha(input_image_path, output_image_path)

    # generateSnow("./textures/SmallRain_back", "./SmallRain_Back.png")
     generateRain("./small_rain_mergedpng", "./MergeImage8x4.png", num_width = 4, num_height = 8)

    # for i in range(1, 11):
    #     input_folder = f"./Lighting/LT{i}PNG"
    #     output_folder = f"./Lighting/LT{i}PNG_resized"
    #     scale_factor = 0.4
    #     compress_images_in_folder(input_folder, output_folder, scale_factor, is_convert_to_white=False)
    #     generateRain(output_folder, f'./lighting{i}.png', num_width = 8, num_height = 4)

    # colors = [
    #     (255, 0, 0),
    #     (0, 255, 0),
    #     (0, 0, 255),
    #     (255, 255, 0)
    # ]
    # create_quadrant_image(800, 600, colors, save_path="quadrant_image.png")
