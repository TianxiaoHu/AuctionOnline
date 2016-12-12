import sys
import socket
import threading
import random
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

def show_tips():
	pass

class Client():
	def __init__(self, server_IP, server_port):
		try:
			self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
			client_IP = '127.0.0.1'
			client_port = random.randint(10000, 65535)
			self.s.bind((client_IP, client_port))
			self.server_address = (server_IP, server_port)
			print 'Client initialized successfully!'
			sys.stdout.flush()
		except:
			print 'Initialization failed, restart the client...'
			sys.stdout.flush()
			sys.exit()

	def receive_message(self):
		message, client_address = self.s.recvfrom(2048)
		plaintext = AESdecrypt(message)
		print plaintext
		sys.stdout.flush()

	def send_message(self, message):
		ciphertext = AESencrypt(message)
		self.s.sendto(ciphertext, self.server_address)
		print message, 'sent to', self.server_address
		sys.stdout.flush()


class ListenerThread(threading.Thread):

	def run(self):
		while True:
			client.receive_message()

class SpeakerThread(threading.Thread):

	def run(self):
		while True:
			data = raw_input()
			if data == 'help':
				show_tips()
			elif data == '/pubmsg':
				msg = raw_input('Input message here:(type q to quit)\n')
				if msg != 'q':
					client.send_message('/pubmsg ' + msg)
				else:
					print 'Quitted'
					sys.stdout.flush()
			elif data[:7] == '/primsg':
				msg = raw_input('Input message here:(type q to quit)\n')
				if msg != 'q':
					client.send_message(data + ' | ' + msg)
				else:
					print 'Quitted'
					sys.stdout.flush()

			else:
				client.send_message(data)

client = Client(ServerIP, ServerPort)


if __name__ == '__main__':
	listener_thread = ListenerThread()
	speaker_thread = SpeakerThread()
	listener_thread.start()
	speaker_thread.start()
