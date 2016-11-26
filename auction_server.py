# -*- coding:utf-8 -*-
import sys
import socket
import threading

global server
global AuctionRoom, User, AddMapID, IDMapAdd
AuctionRoom, User = [], []
AddMapID, IDMapAdd = {}, {}

def user_map_auctions(UserID):
		for room in AuctionRoom:
			if UserID in room.bidder:
				return room
		else:
			print UserID, 'not in any room'
			sys.stdout.flush()

def name_map_auctions(auction_name):
	for room in AuctionRoom:
		if room.name == auction_name:
			return room
	else:
		print auction_name, 'not exist.'
		sys.stdout.flush()


class Room():

	def __init__(self, name, price):
		self.name = name
		self.bidder = []
		self.history = []
		self.highest_price = float(price)
		self.highest_user = ''

	def add_bidder(self, bidder_ID):
		if bidder_ID not in self.bidder:
			self.bidder.append(bidder_ID)
			print bidder_ID, 'successfully joined', self.name
			sys.stdout.flush()
			return True
		else:
			print bidder_ID, 'have been in', self.name
			sys.stdout.flush()
			return False

	def remove_bidder(self, bidder_ID):
		if bidder_ID not in self.bidder:
			print bidder_ID, 'not in', self.name
			sys.stdout.flush()
			return False
		else:
			if self.highest_user != '' and bidder_ID == self.highest_user:
				print bidder_ID, 'bid the highest price!'
				return False
			else:
				self.bidder.remove(bidder_ID)
				print bidder_ID, 'leave from', self.name
				sys.stdout.flush()
				return True

	def draw_bid_history(self):
		return self.history

	def draw_bidder_address(self):
		addresses = []
		for user in self.bidder:
			addresses.append(IDMapAdd[user])
		return addresses

	def update_bid_info(self, UserID, price):
		if price <= self.highest_price:
			print price, 'from', UserID, 'not higher than', self.highest_price
			sys.stdout.flush()
			return False
		else:
			self.highest_price = price
			self.highest_user = UserID
			self.history.append(UserID + ' bid ' + str(price))
			return True


class Server():

	def __init__(self, local_port=20210):

		try:
			local_IP = socket.gethostbyname(socket.gethostname())
			local_address = (local_IP, local_port)
			self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
			self.s.bind(local_address)
			print 'AuctionOnline Server Initialized!'
			sys.stdout.flush()

		except:
			print 'Fail to create Server UDP socket...'
			sys.stdout.flush()
			sys.exit()

	def receive_message(self):
		message, address = self.s.recvfrom(2048)
		print "received:", message, "from", address
		sys.stdout.flush()
		return message, address

	def send_message(self, message, address):
		self.s.sendto(message, address)
		print message, 'sent to', address
		sys.stdout.flush()

	def broadcast(self, message, client_addresses):
		print 'Broadcasting...'
		sys.stdout.flush()
		for client_address in client_addresses:
			self.send_message(message, client_address)
		print 'Broadcasting ended!'
		sys.stdout.flush()

	def deal_client_command(self, message, address):
		fields = message.split(' ')
		if fields[0] in ['/login', '/auctions', '/list', '/join', '/bid', '/leave',
						 '/exit']:
			if fields[0] == '/login':
				try:
					if fields[1] in User:
						self.send_message('Username occupied, try another..', address)
					else:
						User.append(fields[1])
						IDMapAdd[fields[1]] = address
						AddMapID[address] = fields[1]
						print fields[1], 'logged in from', address
						sys.stdout.flush()
				except:
					self.send_message('Invalid input! Type \'help\' for help..', address)

			if fields[0] == '/auctions':
				self.send_message('Next are available auction rooms:', address)
				for room in AuctionRoom:
					self.send_message(room.name, address)

			if fields[0] == '/list':
				try:
					room = user_map_auctions(AddMapID[address])
					roomhistory = room.draw_bid_history()
					if len(roomhistory) == 0:
						self.send_message('No bid history..', address)
					else:
						for bidhistory in roomhistory:
							self.send_message(bidhistory, address)
				except:
					print AddMapID[address], 'haven\'t join a room..'
					sys.stdout.flush()
					self.send_message('You must join a room first..', address)

			if fields[0] == '/join':
				try:
					for room in AuctionRoom:
						if fields[1] == room.name:
							if room.add_bidder(AddMapID[address]):
								broadcast_message = AddMapID[
									address] + ' joined auction!'
								broadcast_address = room.draw_bidder_address()
								if len(broadcast_address) != 0:
									self.broadcast(broadcast_message, broadcast_address)
							else:
								self.send_message('You have already in this room', address)
							break
					else:
						self.send_message('No this room..try another', address)
				except:
					self.send_message('Invalid input! Type \'help\' for help..', address)

			if fields[0] == '/bid':
				try:
					room = user_map_auctions(AddMapID[address])
					if room.update_bid_info(AddMapID[address], float(fields[1])):
						broadcast_message = AddMapID[address] + ' bid ' + fields[1]
						broadcast_address = room.draw_bidder_address()
						if len(broadcast_address) != 0:
							self.broadcast(broadcast_message, broadcast_address)
					else:
						self.send_message('Your price must higher than history!', address)
				except:
					self.send_message('Enter a room first..', address)

			if fields[0] == '/leave':
				for room in AuctionRoom:
					if AddMapID[address] in room.bidder:
						if room.remove_bidder(AddMapID[address]):
							self.send_message('You have left..', address)
							broadcast_message = AddMapID[
								address] + ' has left..'
							broadcast_address = room.draw_bidder_address()
							if len(broadcast_address) != 0:
								self.broadcast(broadcast_message, broadcast_address)
						else:
							self.send_message('You can\'t leave now!', address)
						break
				else:
					self.send_message('Enter a room first..', address)

			if fields[0] == '/exit':
				for room in AuctionRoom:
					if AddMapID[address] in room.bidder:
						if room.remove_bidder(AddMapID[address]):
							self.send_message('You have left..', address)
							broadcast_message = AddMapID[
								address] + ' has left..'
							broadcast_address = room.draw_bidder_address()
							if len(broadcast_address) != 0:
								self.broadcast(broadcast_message, broadcast_address)
						else:
							self.send_message('You can\'t leave now!', address)
							break
				else:
					self.send_message('Successfully exit from AuctionOnline..', address)
					print AddMapID[address], 'exit'
					sys.stdout.flush()
					User.remove(AddMapID[address])
					IDMapAdd.pop(AddMapID[address])
					AddMapID.pop(address)

		else:
			self.send_message('Invalid input! Type \'help\' for help..', address)

	def deal_server_command(self, message):
		fields = message.split(' ')
		if fields[0] in ['/msg', '/list', '/kickout', '/opennewauction', '/auctions',
						 '/enter', '/close']:
			if fields[0] == '/msg':
				for user in fields[2:]:
					try:
						self.send_message(fields[1], IDMapAdd[user])
					except:
						print 'Fail to send', fields[1], 'to', user
						sys.stdout.flush()

			if fields[0] == '/list':
				print 'Next are available auction rooms:'
				for room in AuctionRoom:
					print room.name
				sys.stdout.flush()

			if fields[0] == '/kickout':
				if fields[1] in User:
					room = user_map_auctions(fields[1])
					if room.remove_bidder(fields[1]):
						print fields[1], 'kicked out!'
						sys.stdout.flush()
						self.send_message('You have been kicked out..', IDMapAdd[fields[1]])
						broadcast_message = fields[1] + ' have been kicked out!'
						broadcast_address = room.draw_bidder_address()
						if len(broadcast_address) != 0:
							self.broadcast(broadcast_message, broadcast_address)
					else:
						print fields[1], 'owns the highest price..'
						sys.stdout.flush()
				else:
					print fields[1], 'doesn\'t exist..'
					sys.stdout.flush()

			if fields[0] == '/opennewauction':
				try:
					newroom = Room(fields[1], fields[2])
					AuctionRoom.append(newroom)
					print 'Successfully created room', fields[1]
					sys.stdout.flush()
				except:
					print 'Invalid input.'
					sys.stdout.flush()


			if fields[0] == '/auctions':
				if len(AuctionRoom) != 0:
					for room in AuctionRoom:
						print room.name
					sys.stdout.flush()
				else:
					print 'No room available now, create one first.'
					sys.stdout.flush()

			if fields[0] == '/enter':
				pass

			if fields[0] == '/close':
				try:
					close_room = name_map_auctions(fields[1])
					if len(close_room.bidder) != 0:
						print 'Users in auction room, can\'t close now.'
						sys.stdout.flush()
					else:
						AuctionRoom.remove(close_room)
						del close_room
				except:
					print 'No auction room named', fields[1]
					sys.stdout.flush()
		else:
			print 'Invalid input!'
			sys.stdout.flush()


class ListenerThread(threading.Thread):

	def run(self):
		while True:
			data, address = server.receive_message()
			server.deal_client_command(data, address)


class SpeakerThread(threading.Thread):

	def run(self):
		while True:
			data = raw_input()
			server.deal_server_command(data)

server = Server()

if __name__ == '__main__':
	listener_thread = ListenerThread()
	speaker_thread = SpeakerThread()
	listener_thread.start()
	speaker_thread.start()
