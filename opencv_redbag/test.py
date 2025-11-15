import cv2
import numpy as np


def process_image():
    # 正确初始化变量
    hmax1 = -1
    hmin1 = 180
    hmax2 = -1
    hmin2 = 180
    smax1 = -1
    smin1 = 255
    smax2 = -1
    smin2 = 255
    vmax1 = -1
    vmin1 = 255
    vmax2 = -1
    vmin2 = 255

    # 读取图片
    image = cv2.imread('pi3.png')
    if image is None:
        print('无法读取图片')
        return

    # 转换到HSV颜色空间
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # 红色在HSV颜色空间中的范围，分两个区间
    lower_red1 = np.array([0, 133, 100])
    upper_red1 = np.array([2, 255, 255])
    lower_red2 = np.array([179, 100, 100])
    upper_red2 = np.array([180, 255, 255])

    # 创建掩膜
    mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
    mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
    mask = cv2.bitwise_or(mask1, mask2)

    # 去掉非红色部分
    result = cv2.bitwise_and(image, image, mask=mask)

    # 打印红色部分的HSV值范围
    print("红色部分的HSV值范围（大致）：")
    print("第一个区间：lower =", lower_red1, "upper =", upper_red1)
    print("第二个区间：lower =", lower_red2, "upper =", upper_red2)

    # 遍历像素
    height, width = image.shape[:2]
    for y in range(height):
        for x in range(width):
            if mask[y, x] > 0:  # 仅处理掩膜中为红色的像素
                h, s, v = hsv[y, x]
                if 0 <= h <= 10:
                    if h > hmax1:
                        hmax1 = h
                    if h < hmin1:
                        hmin1 = h
                    if s > smax1:
                        smax1 = s
                    if s < smin1:
                        smin1 = s
                    if v > vmax1:
                        vmax1 = v
                    if v < vmin1:
                        vmin1 = v
                elif 160 <= h <= 179:
                    if h > hmax2:
                        hmax2 = h
                    if h < hmin2:
                        hmin2 = h
                    if s > smax2:
                        smax2 = s
                    if s < smin2:
                        smin2 = s
                    if v > vmax2:
                        vmax2 = v
                    if v < vmin2:
                        vmin2 = v

    # 显示结果
    cv2.imshow('Result', result)
    print("hsvmanmin12", hmax1, hmin1, smax1, smin1, vmax1, vmin1, hmax2, hmin2, smax2, smin2, vmax2, vmin2)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


if __name__ == '__main__':
    process_image()

