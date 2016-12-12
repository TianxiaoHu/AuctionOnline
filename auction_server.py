# -*- coding:utf-8 -*-
import sys
import socket
import threading
from Crypto.Cipher import AES

global server
global AuctionRoom, User, AddMapID, IDMapAdd
AuctionRoom, User = [], []
AddMapID, IDMapAdd = {}, {}

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

def user_exist(UserAddr):
	if UserAddr in IDMapAdd.values():
		return True
	else:
		return False

class Room():

	def __init__(self, name, baseprice, ceilprice, gap):
		self.name = name
		self.bidder = []
		self.history = []
		self.baseprice = float(baseprice)
		self.highest_price = float(baseprice)
		self.highest_user = ''
		self.ceiling = float(ceilprice)
		self.gap = float(gap)

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

	def draw_bidder_ID(self):
		bidder_IDs = []
		for user in self.bidder:
			bidder_IDs.append(user)
		return bidder_IDs

	def update_bid_info(self, UserID, price):
		flag = 0
		info = 0
		if price < self.highest_price + self.gap:
			print price, 'from', UserID, 'not higher than', self.highest_price + self.gap
			sys.stdout.flush()
			flag = 1
			info = self.highest_price + self.gap
			return flag, info
		elif price > self.ceiling:
			print price, 'from', UserID, 'too high! The ceiling price is', self.ceiling
			flag = 2
			info = self.ceiling
			return flag, info
		else:
			self.highest_price = price
			self.highest_user = UserID
			self.history.append(UserID + ' bid ' + str(price))
			flag = 0
			info = price
			return flag, info


class Server():

	def __init__(self, local_port=20210):

		try:
			local_IP = '127.0.0.1'
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
		plaintext = AESdecrypt(message)
		print "received:", plaintext, "from", address
		sys.stdout.flush()
		return plaintext, address

	def send_message(self, message, address):
		ciphertext = AESencrypt(message)
		self.s.sendto(ciphertext, address)
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
		if fields[0] in ['/login', '/auctions', '/join', '/list', '/bidder', '/bid',
		                 '/pubmsg', '/primsg', '/leave', '/exit']:
			if fields[0] == '/login':
				try:
					if user_exist(address):
						self.send_message('You have already logged in! Exit first..', address)
						print address, ' duplicate login refused.'
						sys.stdout.flush()
					else:
						if fields[1] in User:
							self.send_message('Username occupied, try another..', address)
						else:
							User.append(fields[1])
							IDMapAdd[fields[1]] = address
							AddMapID[address] = fields[1]
							self.send_message('Successfully logged in!', address)
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
								broadcast_message = AddMapID[address] + ' joined auction!'
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

			if fields[0] == '/bidder':
				try:
					room = user_map_auctions(AddMapID[address])
					bidders = room.draw_bidder_ID()
					self.send_message('Next are bidders in the room', address)
					for bidder in bidders:
						self.send_message(bidder, address)
				except:
					self.send_message('Enter a room first..', address)

			if fields[0] == '/bid':
				try:
					room = user_map_auctions(AddMapID[address])
					flag, info = room.update_bid_info(AddMapID[address], float(fields[1]))
					if flag == 0:
						broadcast_message = AddMapID[address] + ' bid ' + fields[1]
						broadcast_address = room.draw_bidder_address()
						if len(broadcast_address) != 0:
							self.broadcast(broadcast_message, broadcast_address)
					elif flag == 1:
						self.send_message('Price refused! Please bid higher than '+str(info), address)
					elif flag == 2:
						self.send_message('Price refused! You must bid below the ceiling price '+str(info), address)
				except:
					self.send_message('Enter a room first..', address)

			if fields[0] == '/pubmsg':
				message = ' '.join(fields[1:])
				try:
					room = user_map_auctions(AddMapID[address])
					user_in_room = room.draw_bidder_address()
					self.broadcast('[' + AddMapID[address] + ']:' + message, user_in_room)
				except:
					self.send_message('Enter a room first..', address)

			if fields[0] == '/primsg':
				sep = fields.index('|')
				message = ' '.join(fields[sep+1:])
				try:
					room = user_map_auctions(AddMapID[address])
					user_in_room = room.draw_bidder_address()
					for user in fields[1:sep]:
						if user in IDMapAdd.keys():
							if IDMapAdd[user] in user_in_room:
								self.send_message('[' + AddMapID[address] + ']:' + message, IDMapAdd[user])
							else:
								self.send_message('No user in the room', address)
						else:
							self.send_message('The user may not exist, try again.', address)
				except:
					self.send_message('Invalid input! Type \'help\' for help..', address)

			if fields[0] == '/leave':
				for room in AuctionRoom:
					if AddMapID[address] in room.bidder:
						if room.remove_bidder(AddMapID[address]):
							self.send_message('You have left..', address)
							broadcast_message = AddMapID[address] + ' has left..'
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
						 '/enter', '/close', '/broadcast', '/restart']:
			if fields[0] == '/msg':
				message = raw_input('Input message here:(type q to quit)\n')
				if message != 'q':
					for user in fields[1:]:
						try:
							self.send_message('[Server]:' + message, IDMapAdd[user])
						except:
							print 'Fail to send message to', user
							sys.stdout.flush()
				else:
					print 'Quitted.'
					sys.stdout.flush()

			if fields[0] == '/list':
				pass
				# TODO

			if fields[0] == '/kickout':
				for user in fields[1:]:
					if user in User:
						room = user_map_auctions(user)
						if room.remove_bidder(user):
							print user, 'kicked out!'
							sys.stdout.flush()
							self.send_message('You have been kicked out..', IDMapAdd[user])
							broadcast_message = user + ' have been kicked out!'
							broadcast_address = room.draw_bidder_address()
							if len(broadcast_address) != 0:
								self.broadcast(broadcast_message, broadcast_address)
					else:
						print user, 'doesn\'t exist..'
						sys.stdout.flush()

			if fields[0] == '/opennewauction':
				try:
					newroom = Room(fields[1], fields[2], fields[3], fields[4])
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
				# TODO

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

			if fields[0] == '/broadcast':
				message = raw_input('Input message here:(type q to quit)\n')
				if message != 'q':
					for room_name in fields[1:]:
						try:
							room = name_map_auctions(room_name)
							user_in_room = room.draw_bidder_address()
							self.broadcast('[Server]:' + message, user_in_room)
						except:
							print 'Fail to broadcast to', room_name
							sys.stdout.flush()
				else:
					print 'Quitted.'
					sys.stdout.flush()
			if fields[0] == '/restart':
				try:
					close_room = name_map_auctions(fields[1])
					close_room.history = []
					close_room.highest_price = float(close_room.baseprice)
					close_room.highest_user = ''
					broadcast_message = 'Auction RESTARTED, all bid history cleared!'
					self.broadcast(broadcast_message, close_room.draw_bidder_address())
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
