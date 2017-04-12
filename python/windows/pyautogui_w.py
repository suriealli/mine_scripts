#!/usr/local/env python
#coding:utf-8

import pyautogui
# 原点为左上角，x正方向:右，y正方向:下

# 获取屏幕分辨率
# print pyautogui.size()

# 根据像素移动鼠标 x,y,t  t为多少时间内移动到指定地点 
# pyautogui.moveTo(100,100,duration = 0.1)

# 根据当前位置相对移动鼠标
# pyautogui.moveRel(100,100,duration = 1)

# 获取鼠标当前位置
# print pyautogui.position()

# 用于控制鼠标点击和拖拽
# pyautogui.click(1556, 93,10)

# 鼠标左键按住后移动到位置
# pyautogui.dragTo(1556, 93,3)

# 鼠标左键按住后移动到相对当前鼠标的位置
# pyautogui.dragRel(-156,-93, 3)

# 滚屏，正数向上，负数向下
# pyautogui.scroll(-10)

# 键入文本, -- 移动，点击，输入
# pyautogui.moveTo(1740, 900,duration = 1)
# pyautogui.click()
# pyautogui.typewrite("What are you fucking about??\n")

# 敲击按键，依次敲击
# pyautogui.typewrite(['a','enter','delete'])

# 热键组合
# pyautogui.hotkey("ctrl",'space')