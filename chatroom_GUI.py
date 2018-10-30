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
#  <kafkal>

import json
import sys
import threading
from datetime import datetime

from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtWidgets import QMessageBox

from chatroom_file import chatroom_client,chatroom_ui,chatroom_server,login_ui

class MainWin(chatroom_ui.Ui_MainWindow):
    def __init__(self,MainWindow):
        super().setupUi(MainWindow)
        self.sendButton.clicked.connect(self.send_data)
        self.psendButton.clicked.connect(self.p_send)
        self.logoutButton.clicked.connect(self.logout)
        self.listWidget.doubleClicked.connect(self.choose_p)
        MainWindow.setWindowTitle(username)

    def deal_data(self):
        while True:
            try:
                s = recv_data_list.pop(0)
            except BaseException:
                pass
            else:
                js = json.loads(s)
                if js['status'] == 'chat':
                    msg = js['username'] + '  ' + js['time'] + '\n' + js['data']
                    self.textBrowser.append(msg)
                elif js['status'] == 'userlist':
                    self.listWidget.clear()
                    users = js['users']
                    for i in users:
                        self.listWidget.addItem(i)
                elif js['status'] == 'p_chat':
                    msg = js['username'] + '  ' + js['time'] + '\n' + js['data']
                    self.textBrowser_2.append(msg)
                    if js['data'] == '对方已下线' and js['username'] == '[System]':
                        self.lineEdit.clear()

    def send_data(self):
        s = self.textEdit.toPlainText()
        if s != '':
            chatroom_client.send(sock, s, username)
        else:
            print('no message')
        self.textEdit.clear()

    def logout(self):
        MainWindow.close()

    def p_send(self):
        s = self.textEdit_2.toPlainText()
        othersname = self.lineEdit.text()
        if s != '' and othersname != '':
            now = datetime.now()
            time = now.strftime('%H:%M:%S')
            chatroom_client.p_chat(sock, s, username, othersname, time)
            self.textBrowser_2.append('[Yourself] to '+othersname+'   '+time+'\n'+s)
            self.textEdit_2.clear()
        elif s=='':
            reply = QMessageBox.about(self,'提示','没有输入消息！')
        elif othersname == '':
            reply = QMessageBox.about(self,'提示','没有选择私聊对象！')

    def choose_p(self):
        a = self.listWidget.selectedItems()
        name = a[0].text()
        self.lineEdit.setText(name)

class Login_Window(login_ui.Ui_Dialog):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(400, 300)
        self.form = Dialog
        self.label = QtWidgets.QLabel(Dialog)
        self.label.setGeometry(QtCore.QRect(80, 70, 51, 21))
        font = QtGui.QFont()
        font.setFamily("Adobe Arabic")
        font.setPointSize(10)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.label_2 = QtWidgets.QLabel(Dialog)
        self.label_2.setGeometry(QtCore.QRect(80, 130, 51, 21))
        font = QtGui.QFont()
        font.setFamily("Adobe Arabic")
        font.setPointSize(10)
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")
        self.lineEdit = QtWidgets.QLineEdit(Dialog)
        self.lineEdit.setGeometry(QtCore.QRect(130, 70, 181, 21))
        self.lineEdit.setObjectName("lineEdit")
        self.lineEdit_2 = QtWidgets.QLineEdit(Dialog)
        self.lineEdit_2.setGeometry(QtCore.QRect(130, 130, 181, 21))
        self.lineEdit_2.setObjectName("lineEdit_2")
        self.pushButton = QtWidgets.QPushButton(Dialog)
        self.pushButton.setGeometry(QtCore.QRect(160, 190, 93, 28))
        self.pushButton.setObjectName("pushButton")
        self.pushButton.clicked.connect(self.login)
        self.pushButton_2 = QtWidgets.QPushButton(Dialog)
        self.pushButton_2.setGeometry(QtCore.QRect(160, 240, 93, 28))
        self.pushButton_2.setObjectName("pushButton_2")
        self.pushButton_2.clicked.connect(self.regist)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "登陆"))
        self.label.setText(_translate("Dialog", "账号："))
        self.label_2.setText(_translate("Dialog", "密码："))
        self.pushButton.setText(_translate("Dialog", "登陆"))
        self.pushButton_2.setText(_translate("Dialog", "注册"))

    def login(self):
        global username,sock,address
        username = self.lineEdit.text()
        password = self.lineEdit_2.text()
        chatroom_client.login(sock, address, username, password)
        msg = sock.recv(2048).decode('utf-8')
        js = json.loads(msg)
        if js['data'] == '登陆成功！':
            global flag
            reply = QMessageBox.about(self.form,'提示','登陆成功！')
            self.form.close()
            flag=1
        elif js['data'] == '该用户尚未注册！':
            reply = QMessageBox.about(self.form,'提示','该用户尚未注册！')
            self.lineEdit.clear()
            self.lineEdit_2.clear()
        elif js['data'] == '密码错误！':
            reply = QMessageBox.about(self.form, '提示', '密码错误！')
            self.lineEdit_2.clear()
        elif js['data'] == '该用户已登陆！':
            reply = QMessageBox.about(self.form,'提示','该用户已登陆！')
            self.lineEdit.clear()
            self.lineEdit_2.clear()

    def regist(self):
        global username,sock,address
        username = self.lineEdit.text()
        password = self.lineEdit_2.text()
        chatroom_client.regist(sock, address, username, password)
        msg = sock.recv(2048).decode('utf-8')
        js = json.loads(msg)
        if js['data'] == '注册成功！已登陆':
            global flag
            reply = QMessageBox.about(self.form, '提示', '注册成功！已登陆')
            self.form.close()
            flag = 1
        elif js['data'] == '该用户名已被使用':
            reply = QMessageBox.about(self.form, '提示', '该用户名已被使用')
            self.lineEdit.clear()
            self.lineEdit_2.clear()

class Main_Window(QtWidgets.QMainWindow):
    #重写closeEvent方法，关闭窗口时注销
    def closeEvent(self, *args, **kwargs):
        chatroom_client.logout(sock, username)

if __name__ == '__main__':
    recv_data_list = []
    username = ''
    flag = 0
    # 创建套接字 sock 及 客户端地址 address
    sock, address = chatroom_client.create_socket(1062)
    app = QtWidgets.QApplication(sys.argv)
    login_window = Login_Window()
    login_dialog = QtWidgets.QDialog()
    login_window.setupUi(login_dialog)
    login_dialog.exec_()
    while True:
        if  flag == 1:
            break
    MainWindow = Main_Window()
    ui = MainWin(MainWindow)
    MainWindow.show()
    # 接收消息
    recv_thread = threading.Thread(target=chatroom_client.recv, args=(sock, recv_data_list))
    recv_thread.start()
    # 处理消息
    deal_thread = threading.Thread(target=ui.deal_data)
    deal_thread.start()

    sys.exit(app.exec_())
