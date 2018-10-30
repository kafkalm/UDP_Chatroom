#!/usr/bin/env python
#-*- coding:utf-8 -*-

#  我真诚地保证：
#  我自己独立地完成了整个程序从分析、设计到编码的所有工作。
#  如果在上述过程中，我遇到了什么困难而求教于人，那么，我将在程序实习报告中
#  详细地列举我所遇到的问题，以及别人给我的提示。
#  在此，我感谢 XXX, …, XXX对我的启发和帮助。下面的报告中，我还会具体地提到
#  他们在各个方法对我的帮助。
#  我的程序里中凡是引用到其他程序或文档之处，
#  例如教材、课堂笔记、网上的源代码以及其他参考书上的代码段,
#  我都已经在程序的注释里很清楚地注明了引用的出处。

#  我从未没抄袭过别人的程序，也没有盗用别人的程序，
#  不管是修改式的抄袭还是原封不动的抄袭。
#  我编写这个程序，从来没有想过要去破坏或妨碍其他计算机系统的正常运转。
#  <马天波>

import socket
import threading
import json
from datetime import datetime
#服务器地址
server_address = ('127.0.0.1',1060)

#创建套接字
def create_socket(port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('127.0.0.1', port))
    address = sock.getsockname()
    return sock,address
#发送消息
def send(socket,data,username):
    now = datetime.now()
    time = now.strftime('%H:%M:%S')
    js = json.dumps({"data": data, "username": username, "status": "chat","time":time})
    socket.sendto(js.encode('utf-8'), server_address)
#接收消息
def recv(socket,recv_list):
    while True:
        data = socket.recv(2048)
        text = data.decode('utf-8')
        # 添加到消息队列
        recv_list.append(text)
#注册
def regist(socket,address,username,password):
    js = json.dumps({"username":username,"password":password,"status":"regist","address":address})
    socket.sendto(js.encode('utf-8'),server_address)
    return username
#登陆
def login(socket,address,username,password):
    js = json.dumps({"username": username, "password": password, "status": "login", "address": address})
    socket.sendto(js.encode('utf-8'), server_address)
    return username
#注销
def logout(socket,username):
    js = json.dumps({"status": "logout","username":username})
    socket.sendto(js.encode('utf-8'),server_address)
#发送私聊消息
def p_chat(socket,data,username,othersname,time):
    request = json.dumps({"data": data, "username": username, "status": "p_chat","othersname":othersname,"time":time})
    socket.sendto(request.encode('utf-8'),server_address)
