# -*- coding:utf-8 -*-
'''
/msg [bidderID ]
群发和向指定用户发送消息，用以某些提示。 
 /list 
列出某竞拍室中参加竞拍者的情况。
/kickout bidderID 
将某竞拍者踢出游戏，以防止一些捣乱的竞拍者，如长时间不拍卖。并且向参加该棋局中的对方竞拍者发送踢出的消息。
/opennewauction  auctionName  price
开通新的竞拍室，每个竞拍室只有一件商品, 该商品具有一定的起拍价 
/auctions 
列出当前正在进行竞拍的竞拍室。 
/enter auctionName
可以观看某一竞拍室的竞拍情况，可以/list，/kickout bidderID命令。直到使用leave命令离开该竞拍室。
/close auctionName
关闭某一竞拍室。

服务器除了支持这些命令，最好在竞拍的过程中，增加拍卖所必须的功能，
比如实时对参与某一拍品的所有竞拍者广播最新的竞拍价格，及出价者；
要能判断何时结束某一商品的拍卖，最终的拍卖价格，以及拍品所得者。
'''
import sys
import socket


class Server():

    def __init__(self, local_port=20209):
        try:
            local_IP = socket.gethostbyname(socket.gethostname())
            local_address = (local_IP, local_port)

            self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.s.bind(local_address)
            self.client = list()
            print 'Auction Server Here.'
            sys.stdout.flush()

        except:
            print 'Fail to create UDP socket...'
            sys.exit()

    # def send_message(self, message):
    #     self.s.sendto(message, self.server_address)

    def receive_message(self):
        message, client_address = self.s.recvfrom(2048)
        print "received:", message, "from", client_address
        sys.stdout.flush()
        if client_address not in self.client:
            self.client.append(client_address)
            print client_address, 'connected... ID:',
            sys.stdout.flush()

        # self.s.sendto(message, client_address)

    # def send_message(self, message):

if __name__ == '__main__':
    server = Server()
    while True:
        server.receive_message()

