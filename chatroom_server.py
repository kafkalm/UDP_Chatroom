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
import sqlite3
import hashlib
import json
from datetime import datetime

#存放来自不同client的消息的缓存区 公聊
recv_data_list = []
#存放处理完的消息
deal_data_list = []
#存放不同client的地址/用户名
client_address_list = {}

server_address = ('127.0.0.1',1060)

#发送消息
def send(socket):
    while True:
        try:
            #从处理完的消息队列中取出消息
            msg  = deal_data_list.pop(0)
        except BaseException:
            pass
        else:
            msg = msg.encode('utf-8')
            #给所有用户发送消息
            for addr in client_address_list.values():
                socket.sendto(msg,tuple(addr))
#接收消息
def recv(socket):
    while True:
        recv_data = socket.recv(2048)
        recv_text = recv_data.decode('utf-8')
        #将接收到的消息放入缓存区
        recv_data_list.append(recv_text)
#处理消息
def deal(socket):
    while True:
        #取出消息缓存区的第一条消息
        try:
            s = recv_data_list.pop(0)
        except BaseException:
            pass
        else:
            js = json.loads(s)
            if js['status'] == 'regist':
                #连接数据库
                conn = sqlite3.connect('user.db')
                # 操作数据库的游标
                c = conn.cursor()
                # 判断用户名是否已存在
                c.execute("SELECT USERNAME FROM userdata WHERE USERNAME == (?)", (js['username'],))
                num = c.fetchall()
                if num == []:
                    password = hashlib.sha1(js['password'].encode('utf-8')).hexdigest()
                    c.execute("INSERT INTO userdata (USERNAME,PASSWORD,ADDRESS,STATUS) VALUES (?,?,?,?)",
                              (js['username'], password,str(js['address']), True))
                    conn.commit()
                    # 将地址与用户名对应起来
                    client_address_list[js['username']] = js['address']
                    #反馈
                    msg = json.dumps({'data':'注册成功！已登陆','status':'System'})
                    socket.sendto(msg.encode('utf-8'), tuple(js['address']))
                    #更新用户在线列表
                    user_list = []
                    for user in client_address_list:
                        user_list.append(user)
                    userlist = json.dumps({'users':user_list,'status':'userlist'})
                    for addr in client_address_list.values():
                        socket.sendto(userlist.encode('utf-8'),tuple(addr))
                else:
                    msg = json.dumps({'data': '该用户名已被使用', 'status': 'System'})
                    socket.sendto(msg.encode('utf-8'), tuple(js['address']))
                c.close()
                conn.close()
            elif js['status'] == 'login':
                # 连接数据库
                conn = sqlite3.connect('user.db')
                # 操作数据库的游标
                c = conn.cursor()
                # 判断用户名是否已存在/存在则查询密码
                c.execute("SELECT USERNAME,PASSWORD,STATUS FROM userdata WHERE USERNAME == (?)", (js['username'],))
                num = c.fetchall()
                if num == []:
                    msg = json.dumps({'data': '该用户尚未注册！', 'status': 'System'})
                    socket.sendto(msg.encode('utf-8'), tuple(js['address']))
                elif num[0][2] == 1:
                    msg = json.dumps({'data': '该用户已登陆！', 'status': 'System'})
                    socket.sendto(msg.encode('utf-8'), tuple(js['address']))
                else:
                    password = hashlib.sha1(js['password'].encode('utf-8')).hexdigest()
                    if password == num[0][1]:
                        c.execute("UPDATE userdata SET ADDRESS = (?),STATUS = 1 WHERE USERNAME = (?)", (str(js['address']),js['username']))
                        conn.commit()
                        #将地址与用户名对应起来
                        client_address_list[js['username']] = js['address']
                        msg = json.dumps({'data': '登陆成功！', 'status': 'System'})
                        socket.sendto(msg.encode('utf-8'), tuple(js['address']))
                        user_list = []
                        for user in client_address_list:
                            user_list.append(user)
                        userlist = json.dumps({'users': user_list, 'status': 'userlist'})
                        for addr in client_address_list.values():
                            socket.sendto(userlist.encode('utf-8'), tuple(addr))
                    else:
                        msg = json.dumps({'data': '密码错误！', 'status': 'System'})
                        socket.sendto(msg.encode('utf-8'), tuple(js['address']))
                c.close()
                conn.close()
            elif js['status'] == 'logout':
                client_address_list.pop(js['username'])
                conn = sqlite3.connect('user.db')
                c = conn.cursor()
                #将地址删去 在线状态改为不在线
                c.execute("UPDATE userdata SET ADDRESS = NULL ,STATUS = 0 WHERE USERNAME = (?)", (js['username'],))
                conn.commit()
                user_list = []
                for user in client_address_list:
                    user_list.append(user)
                userlist = json.dumps({'users': user_list, 'status': 'userlist'})
                for addr in client_address_list.values():
                    socket.sendto(userlist.encode('utf-8'), tuple(addr))
            elif js['status'] == 'p_chat':
                try:
                    print(client_address_list)
                    other_addr = client_address_list[js['othersname']]
                    print(other_addr)
                except BaseException:
                    addr = client_address_list[js['username']]
                    print(addr)
                    now = datetime.now()
                    time = now.strftime('%H:%M:%S')
                    s = json.dumps({'data':'对方已下线','username':'[System]','time':time,'status':'p_chat'})
                    print(s)
                    socket.sendto(s.encode('utf-8'),tuple(addr))
                else:
                    socket.sendto(s.encode('utf-8'),tuple(other_addr))
            else:
                #公聊消息无需处理添加到处理完的队列
                deal_data_list.append(s)

if __name__ == '__main__':
    sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    sock.bind(server_address)
    #创建线程接收数据
    recv_thread = threading.Thread(target=recv,args=(sock,))
    #创建线程处理数据
    deal_thread = threading.Thread(target=deal,args=(sock,))
    #创建线程发送数据
    send_thread = threading.Thread(target=send,args=(sock,))
    recv_thread.start()
    deal_thread.start()
    send_thread.start()
    recv_thread.join()
    deal_thread.join()
    send_thread.join()
    sock.close()


