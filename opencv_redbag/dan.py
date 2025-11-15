import cv2
import numpy as np

# 红色hsv
lower_red1 = np.array([0, 133, 100])
upper_red1 = np.array([2, 255, 255])
lower_red2 = np.array([179, 100, 100])
upper_red2 = np.array([180, 255, 255])
frame = cv2.imread('pi3.png', cv2.IMREAD_COLOR)
    # HSV
hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # 红色掩膜
mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
mask = cv2.bitwise_or(mask1, mask2)
cv2.imwrite('mask.png', mask)

contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

max_perimeter = 0
max_contour = None
# 遍历轮廓计算周长并找出最大周长的轮廓
for contour in contours:
    perimeter = cv2.arcLength(contour, True)
    if perimeter > max_perimeter:
        max_perimeter = perimeter
        max_contour = contour

area = cv2.contourArea(max_contour)   #一般周长大的，面积也大（
# 用绿色圈出最大周长的轮廓
if max_contour is not None:
    cv2.drawContours(frame, [max_contour], -1, (0, 255, 0), 2)
    cv2.imwrite('QQ!.png', frame)     #可以通过图片看看是否约束到所需轮廓
    print("perimeter: ", max_perimeter)
    print("area: ", area)
    cv2.waitKey(0)
