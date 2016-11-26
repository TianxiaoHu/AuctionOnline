import sys
import socket
import threading
import random

global client
ServerIP = socket.gethostbyname(socket.gethostname())
ServerPort = 20210

def show_tips():
	pass

class Client():
	def __init__(self, server_IP, server_port):
		try:
			self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
			client_IP = socket.gethostbyname(socket.gethostname())
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
		print message
		sys.stdout.flush()

	def send_message(self, message):
		self.s.sendto(message, self.server_address)
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
			else:
				client.send_message(data)

client = Client(ServerIP, ServerPort)


if __name__ == '__main__':
	listener_thread = ListenerThread()
	speaker_thread = SpeakerThread()
	listener_thread.start()
	speaker_thread.start()
