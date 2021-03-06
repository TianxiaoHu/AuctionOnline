# -*- coding:utf-8 -*-
import socket
import threading
import random
from Tkinter import *
import tkMessageBox
from Crypto.Cipher import AES

global client
ServerIP = '127.0.0.1'
ServerPort = 20210

padding = '\0'
pad = lambda x: x + (16 - len(x) % 16) * padding
unwrap = lambda x: x.replace('\0', '')
key = '1234567890abcdef'
mode = AES.MODE_ECB
encryptor = AES.new(key, mode)
decryptor = AES.new(key, mode)

def AESencrypt(plaintext):
	plaintext = pad(plaintext)
	return encryptor.encrypt(plaintext)

def AESdecrypt(ciphertext):
	plaintext = decryptor.decrypt(ciphertext)
	return unwrap(plaintext)

global window

class MainGui():
	def __init__(self):
		self.root = Tk()
		self.root.geometry('400x250+150+200')
		self.root.title('AuctionOnline-ClientMode')

		self.help_button = Button(self.root, text='Help', command=self.show_tips)
		self.help_button.pack()

		self.slogan = Label(self.root, text='Input your command here:')
		self.slogan.pack()

		self.command_entry = Entry(self.root)
		self.command_entry.pack()

		self.send_button = Button(self.root, text='Send',
								  command=lambda: client.send_message(self.command_entry.get()))
		self.send_button.pack()

		self.server_message = Text(self.root, height=7, width=40)
		self.server_message.pack()

		self.exit_button = Button(self.root, text='Exit', command=lambda: sys.exit())
		self.exit_button.pack()

	def show_tips(self):

		tips = r'''
Next are available commands:
- /login username
- /auctions
- /join auctionname
- /list
- /bidders
- /bid price
- /pubmsg message
- /primsg username1 username2 | message
- /leave
- /exit

Author: TianxiaoHu
Version: 1.0'''
		tkMessageBox.showinfo('AuctionOnline-help', tips)


window = MainGui()


class Client():
	def __init__(self, server_IP, server_port):
		try:
			self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
			client_IP = '127.0.0.1'
			client_port = random.randint(10000, 65535)
			self.s.bind((client_IP, client_port))
			self.server_address = (server_IP, server_port)
			window.server_message.insert(END, 'Client initialized successfully!\n')
		except:
			sys.exit()

	def receive_message(self):
		message, client_address = self.s.recvfrom(2048)
		plaintext = AESdecrypt(message)
		window.server_message.insert(1.0, plaintext + '\n')

	def send_message(self, message):
		ciphertext = AESencrypt(message)
		self.s.sendto(ciphertext, self.server_address)
		window.command_entry.delete(0, END)

class ListenerThread(threading.Thread):
	def run(self):
		while True:
			client.receive_message()

client = Client(ServerIP, ServerPort)

if __name__ == '__main__':
	listener_thread = ListenerThread()
	listener_thread.setDaemon(True)
	listener_thread.start()
	window.root.mainloop()
