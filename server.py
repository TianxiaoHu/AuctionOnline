# -*- coding:utf-8 -*-
import time
import socket
import threading
from Tkinter import *
import tkMessageBox
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

global window

class MainGui():
	def __init__(self):
		self.root = Tk()
		self.root.geometry('400x550+150+100')
		self.root.title('AuctionOnline-ServerMode')

		self.help_button = Button(self.root, text='Help', command=self.show_tips)
		self.help_button.pack()

		self.slogan = Label(self.root, text='Input your command here:')
		self.slogan.pack()

		self.command_entry = Entry(self.root)
		self.command_entry.pack()

		self.input_button = Button(self.root, text='OK',
								   command=lambda: server.deal_server_command(self.command_entry.get()))
		self.input_button.pack()

		self.error_label = Label(self.root, text='')
		self.error_label.pack()

		self.feedback_message = Text(self.root, height=10, width=40)
		self.feedback_message.pack()

		self.log_label = Label(self.root, text='Application log below:')
		self.log_label.pack()

		self.log_message = Text(self.root, height=12, width=40)
		self.log_message.pack()

		self.clear_log_button = Button(self.root, text='Clear log',
									   command=lambda: self.log_message.delete(1.0, END))
		self.clear_log_button.pack()

		self.exit_button = Button(self.root, text='Exit', command=lambda: sys.exit())
		self.exit_button.pack()

	def show_tips(self):
		tips = r'''
Next are available commands:
- /auctions
- /opennewauction auctionname base gap
- /users
- /list auctionname
- /msg username1 username2 | message
- /broadcast auctionname message
- /kickout username1 username2
- /finish auctionname
- /close auctionname
- /restart auctionname

Author: TianxiaoHu
Version: 1.0'''
		tkMessageBox.showinfo('AuctionOnline-help', tips)

window = MainGui()

def user_map_auctions(UserID):
	for room in AuctionRoom:
		if UserID in room.bidder:
			return room
	else:
		return False

def name_map_auctions(auction_name):
	for room in AuctionRoom:
		if room.name == auction_name:
			return room
	else:
		return False

def user_exist(UserAddr):
	if UserAddr in IDMapAdd.values():
		return True
	else:
		return False

class Room():
	def __init__(self, name, baseprice, gap):
		self.name = name
		self.bidder = []
		self.history = []
		self.base_price = float(baseprice)
		self.highest_price = float(baseprice)
		self.highest_user = ''
		self.gap = float(gap)
		self.closed = False

	def add_bidder(self, bidder_ID):
		if self.closed:
			return False
		if bidder_ID not in self.bidder:
			self.bidder.append(bidder_ID)
			window.feedback_message.insert(1.0, str(bidder_ID) + ' joined ' + self.name + '\n')
			return True
		return False

	def remove_bidder(self, bidder_ID):
		if bidder_ID not in self.bidder:
			window.feedback_message.insert(1.0, bidder_ID + ' not in ' + self.name + '\n')
			return False
		else:
			if self.highest_user != '' and self.closed == False and bidder_ID == self.highest_user:
				window.feedback_message.insert(1.0, bidder_ID + ' bid the highest price!\n')
				return False
			else:
				self.bidder.remove(bidder_ID)
				window.feedback_message.insert(1.0, bidder_ID + ' leave from ' + self.name + '\n')
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
		if self.closed:
			flag = 2
			info = None
		else:
			if price < self.highest_price + self.gap:
				flag = 1
				info = self.highest_price + self.gap
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
			window.feedback_message.insert(1.0, 'AuctionOnline Server Initialized!\n')

		except:
			window.feedback_message.insert(1.0, 'Fail to create Server UDP socket...\n')
			time.sleep(2)
			sys.exit()

	def receive_message(self):
		message, address = self.s.recvfrom(2048)
		plaintext = AESdecrypt(message)
		window.log_message.insert(1.0, 'received: ' + plaintext + ' from '+ str(address) + '\n')
		return plaintext, address

	def send_message(self, message, address):
		ciphertext = AESencrypt(message)
		self.s.sendto(ciphertext, address)
		window.log_message.insert(1.0, message + ' send to ' + str(address) + '\n')

	def broadcast(self, message, client_addresses):
		window.log_message.insert(1.0, 'Broadcasting ended!\n')
		for client_address in client_addresses:
			self.send_message(message, client_address)
		window.log_message.insert(1.0, 'Broadcasting...\n')

	def deal_client_command(self, message, address):
		fields = message.split(' ')
		if fields[0] in ['/login', '/auctions', '/join', '/list', '/bidders', '/bid',
		                 '/pubmsg', '/primsg', '/leave', '/exit']:
			if fields[0] == '/login':
				try:
					if user_exist(address):
						self.send_message('You have already logged in! Exit first..', address)
						window.log_message.insert(1.0, str(address)+' duplicate login refused.\n')
					else:
						if fields[1] in User:
							self.send_message('Username occupied, try another..', address)
						else:
							User.append(fields[1])
							IDMapAdd[fields[1]] = address
							AddMapID[address] = fields[1]
							self.send_message(fields[1] + ' successfully logged in!', address)
							window.log_message.insert(1.0, str(fields[1]) + ' logged in from ' + str(address) + '\n')
				except:
					self.send_message('Invalid input!', address)

			if fields[0] == '/auctions':
				for room in AuctionRoom:
					self.send_message(room.name, address)
				self.send_message('Next are available auction rooms:', address)

			if fields[0] == '/list':
				try:
					room = user_map_auctions(AddMapID[address])
					roomhistory = room.draw_bid_history()
					if len(roomhistory) == 0:
						self.send_message('No bid history..', address)
					else:
						for bidhistory in roomhistory[::-1]:
							self.send_message(bidhistory, address)
					room_msg = 'Base price is ' + str(room.base_price) + ', gap is ' + str(room.gap)
					self.send_message(room_msg, address)
				except:
					self.send_message('You must join a room first..', address)

			if fields[0] == '/join':
				try:
					if user_map_auctions(AddMapID[address]) == False:
						room = name_map_auctions(fields[1])
						if room != False:
							if room.add_bidder(AddMapID[address]):
								room_msg = 'Current price is '+str(room.highest_price)+', gap is '+str(room.gap)
								self.send_message(room_msg, address)
								broadcast_message = AddMapID[address] + ' joined auction!'
								broadcast_address = room.draw_bidder_address()
								self.broadcast(broadcast_message, broadcast_address)
							else:
								self.send_message('Room have been closed..try another', address)
						else:
							self.send_message('No this room..try another', address)
					else:
						self.send_message('You have joined an auction, leave it first', address)
				except:
					self.send_message('Invalid input!', address)

			if fields[0] == '/bidders':
				try:
					room = user_map_auctions(AddMapID[address])
					bidders = room.draw_bidder_ID()
					for bidder in bidders:
						self.send_message(bidder, address)
					self.send_message('Next are bidders in the room', address)
				except:
					self.send_message('You must join a room first..', address)

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
					else:
						self.send_message('Auction closed', address)
				except:
					self.send_message('You must join a room first..', address)

			if fields[0] == '/pubmsg':
				try:
					message = ' '.join(fields[1:])
					try:
						room = user_map_auctions(AddMapID[address])
						user_in_room = room.draw_bidder_address()
						self.broadcast('[' + AddMapID[address] + ']:' + message, user_in_room)
					except:
						self.send_message('You must join a room first..', address)
				except:
					self.send_message('Invalid input!', address)

			if fields[0] == '/primsg':
				try:
					sep = fields.index('|')
					message = ' '.join(fields[sep+1:])
					room = user_map_auctions(AddMapID[address])
					if room != False:
						user_in_room = room.draw_bidder_address()
						for user in fields[1:sep]:
							if user in IDMapAdd.keys():
								if IDMapAdd[user] in user_in_room:
									self.send_message('[' + AddMapID[address] + ']:' + message, IDMapAdd[user])
								else:
									self.send_message('No user ' + user + ' in the room', address)
							else:
								self.send_message('The user ' + user + ' may not exist.. try again', address)
					else:
						self.send_message('You must join a room first..', address)
				except:
					self.send_message('Invalid input!', address)

			if fields[0] == '/leave':
				room = user_map_auctions(AddMapID[address])
				if room != False:
					if room.remove_bidder(AddMapID[address]):
						self.send_message('You have left..', address)
						broadcast_message = AddMapID[address] + ' has left..'
						broadcast_address = room.draw_bidder_address()
						if len(broadcast_address) != 0:
							self.broadcast(broadcast_message, broadcast_address)
					else:
						self.send_message('You can\'t leave now!', address)
				else:
					self.send_message('You must join a room first..', address)

			if fields[0] == '/exit':
				room = user_map_auctions(AddMapID[address])
				if room != False:
					if room.remove_bidder(AddMapID[address]):
						self.send_message('You have left..', address)
						broadcast_message = AddMapID[address] + ' has left..'
						broadcast_address = room.draw_bidder_address()
						if len(broadcast_address) != 0:
							self.broadcast(broadcast_message, broadcast_address)
					else:
						self.send_message('You can\'t leave now!', address)
						return
				self.send_message('Successfully exit from AuctionOnline..', address)
				window.feedback_message.insert(1.0, str(AddMapID[address]) + ' exit\n')
				User.remove(AddMapID[address])
				IDMapAdd.pop(AddMapID[address])
				AddMapID.pop(address)

		else:
			self.send_message('Invalid input!', address)

	def deal_server_command(self, message):
		window.command_entry.delete(0, END)
		window.error_label['text'] = ''
		fields = message.split(' ')
		if fields[0] in ['/msg', '/list', '/kickout', '/opennewauction', '/auctions',
						 '/users', '/finish', '/close', '/broadcast', '/restart']:
			if fields[0] == '/msg':
				try:
					sep = fields.index('|')
					message = ' '.join(fields[sep + 1:])
					for user in fields[1:sep]:
						try:
							self.send_message('[Server]:' + message, IDMapAdd[user])
						except:
							window.feedback_message.insert(1.0, 'Fail to send message to ' + user + '\n')
				except:
					window.error_label['text'] =  'Invalid input.'

			if fields[0] == '/list':
				try:
					room = name_map_auctions(fields[1])
					for history in room.history:
						window.feedback_message.insert(1.0, history + '\n')
					window.feedback_message.insert(1.0, 'Next are bid history:\n')
					for user in room.bidder:
						window.feedback_message.insert(1.0, user + '\t' + str(IDMapAdd[user]) + '\n')
					window.feedback_message.insert(1.0, 'Next are bidders:\n')
					window.feedback_message.insert(1.0, 'Highest price owner:' + room.highest_user + '\n')
					window.feedback_message.insert(1.0, 'Current price:' +  str(room.highest_price) + '\n')
					window.feedback_message.insert(1.0, 'Base price:' + str(room.base_price) + ' Gap:' +  str(room.gap) + '\n')
					window.feedback_message.insert(1.0, '-- Room ' + room.name + ' Summary --\n')
				except:
					window.error_label['text'] = 'No auction room fits input'

			if fields[0] == '/kickout':
				try:
					for user in fields[1:]:
						if user in User:
							room = user_map_auctions(user)
							if room != False:
								if room.remove_bidder(user):
									window.feedback_message.insert(1.0, user + ' kicked out!\n')
									self.send_message('You have been kicked out..', IDMapAdd[user])
									broadcast_message = user + ' have been kicked out!'
									broadcast_address = room.draw_bidder_address()
									if len(broadcast_address) != 0:
										self.broadcast(broadcast_message, broadcast_address)
							else:
								window.feedback_message.insert(1.0, user + ' not in any room\n')
						else:
							window.feedback_message.insert(1.0, str(user) + ' doesn\'t exist\n')
				except:
					window.error_label['text'] = 'Invalid input.'

			if fields[0] == '/opennewauction':
				try:
					if name_map_auctions(fields[1]) == False:
						newroom = Room(fields[1], fields[2], fields[3])
						AuctionRoom.append(newroom)
						window.feedback_message.insert(1.0, 'Successfully created room ' + fields[1] + '\n')
						self.broadcast('New room created: '+fields[1], IDMapAdd.values())
					else:
						window.feedback_message.insert(1.0, 'A room named ' + fields[1] + ' already exist.\n')
				except:
					window.error_label['text'] = 'Invalid input.'

			if fields[0] == '/auctions':
				if len(AuctionRoom) != 0:
					for room in AuctionRoom:
						window.feedback_message.insert(1.0, room.name + '\n')
					window.feedback_message.insert(1.0, 'Next are auction rooms\n')
				else:
					window.feedback_message.insert(1.0, 'No room available now, create one first.\n')

			if fields[0] == '/users':
				for user in User:
					room_in = user_map_auctions(user)
					if room_in != False:
						window.feedback_message.insert(1.0, user + ':' + room_in.name + '\n')
					else:
						window.feedback_message.insert(1.0, user + ' not in any room\n')

			if fields[0] == '/finish':
				try:
					close_room = name_map_auctions(fields[1])
					if close_room.closed:
						window.feedback_message.insert(1.0, 'Auction room has been closed\n')
					else:
						close_room.closed = True
						close_room.history.append(close_room.highest_user + ' wins the auction with price ' + str(close_room.highest_price))
						window.feedback_message.insert(1.0, 'Successfully finish '+ fields[1] + '\n')
						broadcast_message = close_room.highest_user + ' wins the auction with price ' + str(close_room.highest_price)
						broadcast_address = close_room.draw_bidder_address()
						self.broadcast(broadcast_message, broadcast_address)
				except:
					window.error_label['text'] = 'No auction room fits your input'

			if fields[0] == '/close':
				try:
					close_room = name_map_auctions(fields[1])
					if len(close_room.bidder) != 0:
						window.feedback_message.insert(1.0, 'Users in auction room, can\'t close now.\n')
					else:
						AuctionRoom.remove(close_room)
						del close_room
						window.feedback_message.insert(1.0, 'Auction room '+fields[1]+' successfully closed\n')
				except:
					window.error_label['text'] = 'No auction room fits your input'

			if fields[0] == '/broadcast':
				try:
					message = ' '.join(fields[2:])
					try:
						room = name_map_auctions(fields[1])
						user_in_room = room.draw_bidder_address()
						self.broadcast('[Server]:' + message, user_in_room)
					except:
						window.feedback_message.insert(1.0, 'Fail to broadcast to' + fields[1] + '\n')
				except:
					window.error_label['text'] = 'Invalid input.'

			if fields[0] == '/restart':
				try:
					close_room = name_map_auctions(fields[1])
					close_room.history = []
					close_room.highest_price = float(close_room.base_price)
					close_room.highest_user = ''
					broadcast_message = 'Auction RESTARTED, all bid history cleared!'
					self.broadcast(broadcast_message, close_room.draw_bidder_address())
					window.feedback_message.insert(1.0, 'Auction '+fields[1]+' restarted, all bid history cleared.\n')
				except:
					window.error_label['text'] = 'No auction room fits your input'

		else:
			window.error_label['text'] = 'Invalid input!'


class ListenerThread(threading.Thread):

	def run(self):
		while True:
			data, address = server.receive_message()
			server.deal_client_command(data, address)

server = Server()

if __name__ == '__main__':
	listener_thread = ListenerThread()
	listener_thread.setDaemon(True)
	listener_thread.start()
	window.root.mainloop()
