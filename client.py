
import socket
import MetaTrader5 as mt5

FORMAT="utf-8"
HEADER=64
DISCONNECT_MSG='!DISCONNECTED'
port=5050
IP=socket.gethostbyname(socket.gethostname()) #gets the ip server
ADDR=(IP,port)

client=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
client.connect(ADDR)

def send_msg(msg):
    message=msg.encode(FORMAT)
    client.send(message)

scaled = [1,2,3,4,5,6]
send_msg(scaled)