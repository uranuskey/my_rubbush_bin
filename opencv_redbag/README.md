# opencv强取豪夺红包
***仅用于学习opencv***

**代码可以在1920*1080的屏幕上正常运行（大概**
## 关于文件的用法
### test.py
test.py主要用于在hsv上筛选已经领取的红包和未经领取的红包，如

![](/images/未领取的红包.png) ![](/images/已领取的红包.png)
### TEST2.py
TEST2.py主要用于检查筛选效果的查看，如

![](/images/Result.png)

### dan.py
dan.py主要用于在当前屏幕下对于红包页面的周长面积的计算以用于筛选，不是1080p的屏幕要修改参数，如

![](/images/QQ!.png)

和Result.png等二次点击的图也要计算以防阻塞
### final manba.py
1080p可以直接用的程序(一般不会出问题

如果追求更快可以用mss代替pyautogui.screenshot

mss刷新频率在21.8帧左右，pyautogui.screenshot在19.6帧左右（我测的
````
from mss import mss

with mss() as sct:
    sct_img = sct.grab(sct.monitors[1])
    frame = np.array(sct_img)
    frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
````
如果不想用mss也可以
````
    screen = pyautogui.screenshot()
    # BGR
    frame = cv2.cvtColor(np.array(screen), cv2.COLOR_RGB2BGR)
    # HSV
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

````
但论速度还是不如连点器120每秒还是太霸道了(胜在一手省心()

自然也比不过js的真挂（
