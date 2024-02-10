import socket

serv_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #семья и тип сервера в скобках
IP = '127.0.0.1' #socket.gethostbyname(socket.gethostname())
PORT = 1233
serv_socket.bind((IP, PORT)) 
#serv_socket = socket.create_server((IP, PORT)) то же, что и выше - создание самого сервера
serv_socket.listen(4) #кол-во принимаемых запросов для режима ожидания

print('Start working...')
print(IP) 

client, address = serv_socket.accept() #принятие запроса с разделением на клиента и его адрес, ждем сигнала.

data = client.recv(1024).decode('utf8')

print(data)
content = ''
content += "▒▒▒▒▒█▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀█"
content += '\n'
content += "▒▒▒▒▒█░▒▒▒▒▒▒▒▓▒▒▓▒▒▒▒▒▒▒░█"
content += '\n'
content += "▒▒▒▒▒█░▒▒▓▒▒▒▒▒▒▒▒▒▄▄▒▓▒▒░█░▄▄"
content += '\n'
content += "▄▀▀▄▄█░▒▒▒▒▒▒▓▒▒▒▒█░░▀▄▄▄▄▄▀░░█"
content += '\n'
content += "█░░░░█░▒▒▒▒▒▒▒▒▒▒▒█░░░░░░░░░░░█"
content += '\n'
content += "▒▀▀▄▄█░▒▒▒▒▓▒▒▒▓▒█░░░█▒░░░░█▒░░█"
content += '\n'
content += "▒▒▒▒▒█░▒▓▒▒▒▒▓▒▒▒█░░░░░░░▀░░░░░█"
content += '\n'
content += "▒▒▒▄▄█░▒▒▒▓▒▒▒▒▒▒▒█░░█▄▄█▄▄█░░█"
content += '\n'
content += "▒▒▒█░░░█▄▄▄▄▄▄▄▄▄▄█░█▄▄▄▄▄▄▄▄▄█"
content += '\n'
content += "▒▒▒█▄▄█░░█▄▄█░░░░░░█▄▄█░░█▄▄█"
content += '\n'
content += "I've done it, boss <3"
content = content.encode("UTF8")
HDRS = 'HTTP/1.1 200 OK\r\nContent-Type: text/plain;charset=UTF8\r\nConnection: close\r\n'
HDRS += 'Content-Length: ' + str(len(content)) + '\r\n\r\n'
HDRS = HDRS.encode('UTF8')
client.send(HDRS + content)
print('Shutdown...')