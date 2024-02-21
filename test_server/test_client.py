import socket
import os

def start_the_connection():
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #семья и тип соккета в скобках
        IP = '127.0.0.1' #socket.gethostbyname(socket.gethostname())
        PORT = 1233
        client.connect((IP, PORT)) 
        while True:
            request = "GET "
            request += input()
            request = request.encode("utf8")
            client.send(request)
            data = client.recv(1024).decode("utf8")
            print(data)
            client.shutdown(socket.SHUT_WR)
            print("Done!\n\n")
    except KeyboardInterrupt:
        client.close()
        return
        
        
start_the_connection()