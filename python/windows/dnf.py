 # -*- coding: utf-8 -*- # 

import pythoncom
import pyHook
import win32api
import win32con
import time
import threading
import random

def auto_click():
    global mouse_down,mouse_up
    while (1):
        if mouse_down != mouse_up:        
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
            #连射多少秒，大约0.1秒一发子弹
            time.sleep(random.uniform(0.38,0.42))
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
            #连发之间的停顿时间
            time.sleep(random.uniform(0.25,0.29))

def auto_key():
    global key_down,key_up
    while (1):
        if key_down != key_up:        
            win32api.keybd_event(120,0,0,0)
            time.sleep(random.uniform(0.02,0.03))
            win32api.keybd_event(120,0,win32con.KEYEVENT_KEYUP,0) #Realize the X button
            time.sleep(0.01)

def onKeyDownEvent():
    global key_down
    key_down += 1
    print "Key X down" + str(key_down)
    return True

def onKeyUpEvent():
    global key_up
    key_up += 1
    print "Key X up" + str(key_up)
    return True

def onMouse_leftdown(event):
    # 监听鼠标左键按下事件
    global mouse_down
    mouse_down += 1
    print "left DOWN DOWN"+str(mouse_down)
    return True

def onMouse_leftup(event):
    # 监听鼠标左键弹起事件
    global mouse_up
    mouse_up += 1
    print "left UP UP UP"+str(mouse_up)
    return True

def main():
    hm = pyHook.HookManager()

    hm.MouseLeftDown = onMouse_leftdown
    hm.MouseLeftUp = onMouse_leftup
    hm.HookMouse()

    hm.KeyDown = onKeyDownEvent
    hm.KeyUp = onKeyUpEvent
    hm.HookKeyboard()
    
    # 进入循环，如不手动关闭，程序将一直处于监听状态
    pythoncom.PumpMessages()

if __name__ == "__main__":
    mouse_down = 0
    mouse_up = 0
    key_down = 0
    key_up = 0
    # 新线程执行的代码:
    # print('thread %s is running...' % threading.current_thread().name)
    t = threading.Thread(target = auto_click, name='mouse_click')
    tk = threading.Thread(target = auto_key, name = 'key_click')
    t.start()
    tk.start()
    main()