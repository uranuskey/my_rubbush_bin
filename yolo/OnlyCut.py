import os
import shutil
import random


def get_annotated_files(label_folder, image_folder):
    """
    获取已标注的标签文件和对应的图片文件列表
    """
    annotated_labels = []
    annotated_images = []
    for label_file in os.listdir(label_folder):
        label_path = os.path.join(label_folder, label_file)
        if os.path.isfile(label_path):
            image_name = os.path.splitext(label_file)[0] + '.png'
            image_path = os.path.join(image_folder, image_name)
            if os.path.exists(image_path):
                annotated_labels.append(label_path)
                annotated_images.append(image_path)
    return annotated_labels, annotated_images


def split_dataset(annotated_labels, annotated_images, output_base_folder, train_ratio=0.7, valid_ratio=0.2):
    """
    将已标注的数据按照指定比例分配到test、train、valid文件夹中
    """
    num_samples = len(annotated_labels)
    num_train = int(num_samples * train_ratio)
    num_valid = int(num_samples * valid_ratio)
    num_test = num_samples - num_train - num_valid

    # 打乱数据顺序
    indices = list(range(num_samples))
    random.shuffle(indices)

    train_indices = indices[:num_train]
    valid_indices = indices[num_train:num_train + num_valid]
    test_indices = indices[num_train + num_valid:]

    # 创建输出文件夹结构
    train_folder = os.path.join(output_base_folder, 'train')
    valid_folder = os.path.join(output_base_folder, 'valid')
    test_folder = os.path.join(output_base_folder, 'test')
    os.makedirs(train_folder, exist_ok=True)
    os.makedirs(valid_folder, exist_ok=True)
    os.makedirs(test_folder, exist_ok=True)

    train_images_folder = os.path.join(train_folder, 'images')
    train_labels_folder = os.path.join(train_folder, 'labels')
    valid_images_folder = os.path.join(valid_folder, 'images')
    valid_labels_folder = os.path.join(valid_folder, 'labels')
    test_images_folder = os.path.join(test_folder, 'images')
    test_labels_folder = os.path.join(test_folder, 'labels')

    os.makedirs(train_images_folder, exist_ok=True)
    os.makedirs(train_labels_folder, exist_ok=True)
    os.makedirs(valid_images_folder, exist_ok=True)
    os.makedirs(valid_labels_folder, exist_ok=True)
    os.makedirs(test_images_folder, exist_ok=True)
    os.makedirs(test_labels_folder, exist_ok=True)

    # 分配数据到不同文件夹
    for index in train_indices:
        label_path = annotated_labels[index]
        image_path = annotated_images[index]
        shutil.copy2(label_path, train_labels_folder)
        shutil.copy2(image_path, train_images_folder)

    for index in valid_indices:
        label_path = annotated_labels[index]
        image_path = annotated_images[index]
        shutil.copy2(label_path, valid_labels_folder)
        shutil.copy2(image_path, valid_images_folder)

    for index in test_indices:
        label_path = annotated_labels[index]
        image_path = annotated_images[index]
        shutil.copy2(label_path, test_labels_folder)
        shutil.copy2(image_path, test_images_folder)


if __name__ == "__main__":
    # 原始标注文件夹路径和图片文件夹路径

    label_folder = r'new1\yolo\labels_my-project-name_2025-10-20-09-18-38' # 请替换为实际的标签文件夹路径
    image_folder = r'new1\yolo\images'  # 请替换为实际的图片文件夹路径
    import os

    if not os.path.exists(label_folder):
        print(f"路径 {label_folder} 不存在")
        # 进一步处理，如使用默认路径或抛出异常

    # 输出文件夹路径
    output_base_folder = 'new11'  # 请替换为实际的输出文件夹路径

    annotated_labels, annotated_images = get_annotated_files(label_folder, image_folder)
    split_dataset(annotated_labels, annotated_images, output_base_folder)

