# -*- coding:utf-8 -*-
'''
/login bidderName
用bidderName登录服务器。服务方给该用户分配一个唯一标识bidderID
/auctions
列出当前正在进行拍卖的拍卖室
/list
列出某一竞拍室所有参加竞拍者的情况。
 /join auctionName
加入某一竞拍室，服务器为其发送竞拍品目前的竞拍价格，及出价者。室中的所有竞拍者收到其加入的消息。
 /bid price
为当前拍品出价
 /leave
离开某一竞拍室（注意，不能是最终的出价者，如是，服务器提示）。室中的所有竞拍者收到其离开的消息。
'''
import sys
import socket


class Client():

    def __init__(self, server_IP, server_port=20209):
        try:
            self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        except:
            print 'Fail to create UDP socket...'
            sys.exit()

        self.server_IP = server_IP
        self.server_port = server_port
        self.server_address = (server_IP, server_port)

    def send_message(self, message):
        self.s.sendto(message, self.server_address)

    # def receive_message(self):
    #     message, client_address = self.s.recvfrom(2048)
    #     print "received:", message, "from", client_address
    #     self.s.sendto(message, client_address)
    #     sys.stdout.flush()


def main():
    localIP = socket.gethostbyname(socket.gethostname())
    client = Client(localIP)
    while True:
        mess = raw_input()
        client.send_message(mess)
if __name__ == '__main__':
    main()
