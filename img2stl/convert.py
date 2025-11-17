from PIL import Image
import numpy as np
from stl import mesh

def create_stl_from_image(image_path, output_filename, min_thickness=1.0, max_thickness=3.0, base_height=0.5):
    """
    通过灰度图像生成一个带有基座的STL浮雕文件。
    (已修正Y轴翻转问题)

    参数:
    image_path (str): 输入图像的文件路径。
    output_filename (str): 输出STL文件的名称。
    min_thickness (float): 对应图像最亮部分（白色）的浮雕厚度（毫米）。
    max_thickness (float): 对应图像最暗部分（黑色）的浮雕厚度（毫米）。
    base_height (float): 基座的高度（毫米）。
    """
    try:
        # 1. 加载图像并转换为灰度图
        img = Image.open(image_path).convert('L')
        width, height = img.size
        pixels = np.array(img)
        print(f"图像加载成功: {width}x{height} 像素")

        # 2. 将灰度值映射到厚度
        inverted_pixels = 255 - pixels
        normalized_height = inverted_pixels / 255.0
        depth_map = min_thickness + (max_thickness - min_thickness) * normalized_height

        # 3. 创建顶点 (已修正Y轴)
        vertices = np.zeros((height + 1, width + 1, 3))
        for y in range(height + 1):
            for x in range(width + 1):
                # 对四个相邻像素的深度值取平均，以平滑顶点高度
                z = np.mean(depth_map[max(0, y-1):min(height, y+1), max(0, x-1):min(width, x+1)])
                # Y坐标使用 (height - y) 来修正图像上下颠倒的问题
                vertices[y, x] = [x, height - y, z + base_height]

        # 4. 创建面片 (两个三角形组成一个正方形)
        faces = []
        for y in range(height):
            for x in range(width):
                # 定义一个正方形的四个顶点
                v1 = vertices[y, x]
                v2 = vertices[y, x + 1]
                v3 = vertices[y + 1, x]
                v4 = vertices[y + 1, x + 1]

                # 创建两个三角形面片
                faces.append([v1, v3, v2])
                faces.append([v2, v3, v4])

        # 5. 创建底部基座
        base_vertices = np.array([
            [0, 0, 0],
            [width, 0, 0],
            [0, height, 0],
            [width, height, 0]
        ])
        # 基座底部的两个三角形
        faces.append([base_vertices[0], base_vertices[1], base_vertices[2]])
        faces.append([base_vertices[2], base_vertices[1], base_vertices[3]])

        # 6. 创建侧面墙体
        # 顶部边缘
        top_edge_y0 = vertices[0, :, :]      # 图像顶部 (y=height)
        top_edge_yH = vertices[height, :, :] # 图像底部 (y=0)
        top_edge_x0 = vertices[:, 0, :]      # 图像左侧
        top_edge_xW = vertices[:, width, :]  # 图像右侧

        # 底部边缘
        bottom_edge_y0 = np.copy(top_edge_y0)
        bottom_edge_y0[:, 2] = 0
        bottom_edge_yH = np.copy(top_edge_yH)
        bottom_edge_yH[:, 2] = 0
        bottom_edge_x0 = np.copy(top_edge_x0)
        bottom_edge_x0[:, 2] = 0
        bottom_edge_xW = np.copy(top_edge_xW)
        bottom_edge_xW[:, 2] = 0

        # 连接侧面 (此部分逻辑无需更改)
        for i in range(width):
            faces.append([top_edge_y0[i], bottom_edge_y0[i], top_edge_y0[i+1]])
            faces.append([bottom_edge_y0[i], bottom_edge_y0[i+1], top_edge_y0[i+1]])

            faces.append([top_edge_yH[i], top_edge_yH[i+1], bottom_edge_yH[i]])
            faces.append([bottom_edge_yH[i], top_edge_yH[i+1], bottom_edge_yH[i+1]])

        for i in range(height):
            faces.append([top_edge_x0[i], top_edge_x0[i+1], bottom_edge_x0[i]])
            faces.append([bottom_edge_x0[i], top_edge_x0[i+1], bottom_edge_x0[i+1]])

            faces.append([top_edge_xW[i], bottom_edge_xW[i], top_edge_xW[i+1]])
            faces.append([bottom_edge_xW[i], bottom_edge_xW[i+1], top_edge_xW[i+1]])

        # 7. 创建STL模型并保存
        faces_np = np.array(faces)
        relief_mesh = mesh.Mesh(np.zeros(faces_np.shape[0], dtype=mesh.Mesh.dtype))
        for i, f in enumerate(faces_np):
            for j in range(3):
                relief_mesh.vectors[i][j] = f[j]

        relief_mesh.save(output_filename)
        print(f"STL文件 '{output_filename}' 已成功生成！")

    except FileNotFoundError:
        print(f"错误：找不到文件 '{image_path}'。请检查文件路径是否正确。")
    except Exception as e:
        print(f"处理过程中发生错误: {e}")

if __name__ == '__main__':
    # --- 用户配置 ---
    input_image_file = 'img.png'
    output_stl_file = 'output_relief_corrected.stl'

    # --- 调用函数 ---
    create_stl_from_image(input_image_file, output_stl_file,
                           min_thickness=1.0,
                           max_thickness=2.5,
                           base_height=0)
