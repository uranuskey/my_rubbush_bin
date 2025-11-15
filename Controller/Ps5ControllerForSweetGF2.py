#甜蜜女友2，启动
import pygame
import pyautogui
import time
import math
import ctypes  # 用于获取屏幕分辨率

# -------------------------- 1. 初始化（适配PS5手柄） --------------------------
pygame.init()
pygame.joystick.init()

# 禁用PyAutoGUI的安全机制（防止鼠标移到角落报错）
pyautogui.FAILSAFE = False
# 提高PyAutoGUI操作速度
pyautogui.PAUSE = 0.001

# 获取屏幕分辨率用于动态调整速度
user32 = ctypes.windll.user32
SCREEN_WIDTH = user32.GetSystemMetrics(0)
SCREEN_HEIGHT = user32.GetSystemMetrics(1)

# 连接PS5手柄（若连接多个，调整索引0为对应序号）
try:
    joystick = pygame.joystick.Joystick(0)
    joystick.init()
    print(f"已连接PS5手柄：{joystick.get_name()}")
except pygame.error:
    print("未检测到PS5手柄，请检查蓝牙/USB连接")
    exit()

# PS5手柄专属配置（灵敏度、死区适配）
BASE_SPEED = 10  # 基础速度（提高默认值）
MAX_SPEED = 30  # 最大速度（大幅提高）
DEAD_ZONE = 0.1  # 稍减小死区，提高响应
TRIGGER_THRESHOLD = 0.3  # 扳机键触发阈值
KEY_DELAY = 0.03  # 减少按键延迟
SMOOTHING_FACTOR = 0.5  # 降低平滑因子，提高响应速度
UPDATE_INTERVAL = 0.005  # 减少循环间隔，提高更新频率

# 用于平滑处理的变量
prev_x, prev_y = 0, 0

# -------------------------- 2. PS5手柄按键映射表（预设常用键） --------------------------
BUTTON_MAPPING = {
    0: "left_click",  # ×键 → 鼠标左键
    1: "right_click",  # ○键 → 鼠标右键
    2: "keyboard_space",  # □键 → 隐藏对话框
    3: "keyboard_ctrl",  # △键 → 按住文本跳过
    9: "keyboard_f6",  # L1键 → 移动到上一个选项
    10: "keyboard_f7",  # R1键 → 移动到下一个选项
    15: "keyboard_enter",  # 触控板按下 → 键盘回车
    6: "keyboard_esc",  #右上角按键 → esc
    4: "keyboard_tab",  #左上角按键 → 显示后台日志
    7: "keyboard_f8",  #左摇杆按下 → 跳过h场景
    8: "keyboard_f12",  #右摇杆按下 → 最小化
    
    # 方向键映射
    11: "keyboard_f1",   # 上方向键 → 快速存档
    12: "keyboard_f2",   # 下方向键 → 快速读档
    13: "keyboard_f5",   # 左方向键 → 自动速度减慢
    14: "keyboard_f4"    # 右方向键 → 自动速度加快
}


# -------------------------- 3. 核心功能 --------------------------
def get_ps5_joystick_move():
    """读取PS5左摇杆，控制鼠标移动（高速流畅版）"""
    global prev_x, prev_y
    
    left_x = joystick.get_axis(0)  # 左摇杆X轴
    left_y = joystick.get_axis(1)  # 左摇杆Y轴

    # 死区过滤
    if abs(left_x) < DEAD_ZONE:
        left_x = 0
    if abs(left_y) < DEAD_ZONE:
        left_y = 0
    
    # 计算摇杆偏离中心的距离
    magnitude = math.sqrt(left_x**2 + left_y**2)
    
    # 应用改进的加速度曲线：更快速达到高速
    if magnitude > 0:
        # 使用平方曲线替代立方曲线，更快达到高速
        speed_factor = BASE_SPEED + (MAX_SPEED - BASE_SPEED) * (magnitude ** 2)
        
        # 归一化方向
        left_x_normalized = left_x / magnitude
        left_y_normalized = left_y / magnitude
        
        # 计算目标速度
        target_x = left_x_normalized * speed_factor
        target_y = left_y_normalized * speed_factor
        
        # 平滑过渡：使用较低的平滑因子，提高响应性
        smooth_x = prev_x * SMOOTHING_FACTOR + target_x * (1 - SMOOTHING_FACTOR)
        smooth_y = prev_y * SMOOTHING_FACTOR + target_y * (1 - SMOOTHING_FACTOR)
        
        # 更新上一次的移动值
        prev_x, prev_y = smooth_x, smooth_y
        
        return smooth_x, smooth_y
    
    # 如果摇杆在死区内，重置平滑值
    prev_x, prev_y = 0, 0
    return 0, 0

def handle_ps5_right_joystick_as_arrow_keys():
    """读取PS5右摇杆，模拟电脑方向键"""
    right_x = joystick.get_axis(2)  
    right_y = joystick.get_axis(3) 

    # 死区过滤
    dead_zone = 0.4  # 稍减小死区
    right_x = 0 if abs(right_x) < dead_zone else right_x
    right_y = 0 if abs(right_y) < dead_zone else right_y

    # 释放所有方向键
    pyautogui.keyUp('up')
    pyautogui.keyUp('down')
    pyautogui.keyUp('left')
    pyautogui.keyUp('right')

    # 根据摇杆方向按下对应的方向键
    if right_y < -dead_zone:
        pyautogui.keyDown('up')
    elif right_y > dead_zone:
        pyautogui.keyDown('down')

    if right_x < -dead_zone:
        pyautogui.keyDown('left')
    elif right_x > dead_zone:
        pyautogui.keyDown('right')


def get_ps5_trigger():
    """读取PS5扳机键（L2=滚轮上滚，R2=滚轮下滚）"""
    l2_value = joystick.get_axis(2)
    r2_value = joystick.get_axis(5)

    # 增加滚轮速度
    scroll_amount = 2 if l2_value > TRIGGER_THRESHOLD * 1.5 else 1
    if l2_value > TRIGGER_THRESHOLD:
        pyautogui.scroll(scroll_amount)
    elif r2_value > TRIGGER_THRESHOLD:
        pyautogui.scroll(-scroll_amount)


# -------------------------- 4. 主循环（监听PS5手柄输入） --------------------------
print("PS5手柄模拟键鼠已启动（按 Ctrl+C 退出）")
print(f"屏幕分辨率: {SCREEN_WIDTH}x{SCREEN_HEIGHT} - 已优化速度适配")
try:
    while True:
        # 处理摇杆→鼠标移动
        move_x, move_y = get_ps5_joystick_move()
        if move_x != 0 or move_y != 0:
            # 使用pyautogui的duration参数实现更平滑的移动
            pyautogui.moveRel(move_x, move_y, duration=UPDATE_INTERVAL)

        handle_ps5_right_joystick_as_arrow_keys()

        # 处理扳机键→滚轮
        get_ps5_trigger()

        # 处理按键→键鼠操作
        for event in pygame.event.get():
            if event.type == pygame.JOYBUTTONDOWN:
                button_id = event.button
                if button_id in BUTTON_MAPPING:
                    action = BUTTON_MAPPING[button_id]
                    if action.startswith("keyboard_"):
                        pyautogui.press(action.split("_")[1])
                        time.sleep(KEY_DELAY)
                    else:
                        pyautogui.click(button=action.split("_")[0])
                        time.sleep(KEY_DELAY)

        # 减少循环间隔，提高响应速度
        time.sleep(UPDATE_INTERVAL)
except KeyboardInterrupt:
    print("程序已退出")
finally:
    joystick.quit()
    pygame.quit()
    
