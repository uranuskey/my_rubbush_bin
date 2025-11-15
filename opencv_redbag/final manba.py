#opencv在1080p的屏幕下抢QQ红包，注释的代码是调试用
#vx红包改一下红包参数和筛选hsv的范围就行了(大概
#仅供学习opencv使用，请勿以此牟利(我已经把红包散财回去了，论速度肯定不如真挂，但是连点器乱点进入小广告也避免了(

import cv2
import numpy as np
import pyautogui
import time
from mss import mss
from threading import Timer

# 红色hsv，保留未抢的红包，筛选抢过的红包
lower_red1 = np.array([0, 133, 100])
upper_red1 = np.array([2, 255, 255])
lower_red2 = np.array([179, 100, 100])
upper_red2 = np.array([180, 255, 255])

#红包参数（分辨率不同要乘一个系数，1920*1080）
target_width = 150
target_height = 230
width_lower_bound = target_width * 0.8
width_upper_bound = target_width * 1.2
height_lower_bound = target_height * 0.8
height_upper_bound = target_height * 1.2

# 标志位
sign = 0
tick = 0

def contours_check(contours):

    max_perimeter = 0
    max_contour = None
    area = 0

    # 遍历轮廓,最大周长
    for contour in contours:
        perimeter = cv2.arcLength(contour, True)
        if perimeter > max_perimeter:
            max_perimeter = perimeter
            max_contour = contour
            area = cv2.contourArea(max_contour)

    # 周长（1080最小至少为1188.7,最大在2371）,面积大于27600
    #print("area=",area)
    #print("max_perimeter=",max_perimeter)
    if max_contour is not None and 1180*0.9<=max_perimeter<=2371*1.1 and area > 27600:
        #print("判定为通过")
        return max_contour
    else:
        return False

def open_redbag(contours):

    for contour in contours:
        # 轮廓外接矩形
        x, y, w, h = cv2.boundingRect(contour)
        if width_lower_bound <= w <= width_upper_bound and height_lower_bound <= h <= height_upper_bound:
            # 轮廓的矩
            M = cv2.moments(contour)
            if M["m00"] != 0:
                # 红色区域中心坐标
                cX = int(M["m10"] / M["m00"])
                cY = int(M["m01"] / M["m00"])
                # 在图像上绘制中心坐标点
                cv2.circle(frame, (cX, cY), 5, (0, 255, 0), -1)
                # 模拟点击红色区域的正中央
                #pyautogui.moveTo(cX, cY)   #先移动再点吗？不赖。其实注释掉也没有任何影响，甚至更快（
                pyautogui.click(cX, cY)
                #print('cX:', cX, 'cY:', cY)
                return True
            else:
                return False

def close_redbag(contours):

        x, y, w, h = cv2.boundingRect(contours)
        #roi = mask[y:y + h, x:x + w]   检测识别用的roi，imshow
        # 模拟鼠标点击匹配中心
        pyautogui.click(x + 450, y + 20)
        #print('X:', x + 450, 'Y:', y + 20)

def check_obstruction(contours):    #检查阻塞

    if np.any(contours_check(contours)):
        close_redbag(contours_check(contours))

def run_5ps():        #
    check_obstruction(contours)
    timer = Timer(5, run_5ps)   #每隔5秒检查一下是否被红包页面卡死
    #print(counter)                    #测刷新率用
    timer.start()

#主函数
#counter = 0
while True:
    global bool_red
    bool_red = False

    with mss() as sct:
        sct_img = sct.grab(sct.monitors[1])
        frame = np.array(sct_img)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # 红色掩膜
    mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
    mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
    mask = cv2.bitwise_or(mask1, mask2)
    #cv2.imwrite('mask.png', mask)

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cv2.drawContours(frame, contours, 0, (0, 255, 0), 2)
    #cv2.imwrite('ft7.png', frame)
    if tick == 0:
        run_5ps()     #防止退出红包失败阻塞程序运行
        tick = 1

    if sign == 0:
        bool_red = open_redbag(contours) #识别并点击红包

    if bool_red is True and sign == 0: # 已经点击，应判断是否是红包
        sign = 1
        time.sleep(1)    #等待红包页面加载，可根据配置适当更改
        #print("跳过一轮")
        continue                       #刷新识别页面

    elif sign == 1:
        #print("开始判断红包")
        if np.any(contours_check(contours)):  # 已判断是红包页面
            #print("是红包")
            #cv2.imwrite('frame.png', frame)
            close_redbag(contours_check(contours))  #退出红包页面
        else: #不是红包页面
            sign = 0
            #print("不是红包")
    #counter += 1
    # 按下q键退出循环
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
