import cv2
import numpy as np


def process_image():
    # 读取图片
    image = cv2.imread('2.png')
    if image is None:
        print('无法读取图片')
        return
    # 转换到HSV颜色空间
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    # 红色在HSV颜色空间中的范围，分两个区间
    lower_red1 = np.array([0, 133, 100])
    upper_red1 = np.array([2, 255, 255])
    lower_red2 = np.array([179, 133, 100])
    upper_red2 = np.array([180, 255, 255])
    # 创建掩膜
    mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
    mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
    mask = cv2.bitwise_or(mask1, mask2)
    # 去掉非红色部分
    result = cv2.bitwise_and(image, image, mask = mask)
    # 打印红色部分的HSV值范围
    print("红色部分的HSV值范围（大致）：")
    print("第一个区间：lower =", lower_red1, "upper =", upper_red1)
    print("第二个区间：lower =", lower_red2, "upper =", upper_red2)
    # 显示结果
    cv2.imwrite('Result.png', result)
    cv2.waitKey(0)
    cv2.destroyAllWindows(

    )


process_image()


