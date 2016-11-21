import sys
import socket
import threading


class Listener:

    def __init__(self, local_port=20210):
        try:
            local_IP = socket.gethostbyname(socket.gethostname())
            local_address = (local_IP, local_port)
            self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.s.bind(local_address)
            print 'Lisenter Initialized!'
            sys.stdout.flush()

        except:
            print 'Fail to create Listener UDP socket...'
            sys.stdout.flush()
            sys.exit()

    def receive_message(self):
        message, speaker_address = self.s.recvfrom(2048)
        print "received:", message, "from", speaker_address
        sys.stdout.flush()


class ListenerThread(threading.Thread):

    def run(self):
        listener = Listener()
        while True:
            listener.receive_message()


class Speaker:

    def __init__(self, server_IP, server_port):
        try:
            self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            print 'Speaker Initialized!'
            sys.stdout.flush()
        except:
            print 'Fail to create Speaker UDP socket...'
            sys.stdout.flush()
            sys.exit()

        self.server_address = (server_IP, server_port)

    def send_message(self, message):
        self.s.sendto(message, self.server_address)
        print message, 'sent!', self.server_address
        sys.stdout.flush()


class SpeakerThread(threading.Thread):

    def run(self):
        local_IP = socket.gethostbyname(socket.gethostname())
        speaker = Speaker(local_IP, 20210)
        while True:
            data = raw_input()
            speaker.send_message(data)

if __name__ == '__main__':
    a = ListenerThread()
    b = SpeakerThread()
    a.start()
    b.start()
