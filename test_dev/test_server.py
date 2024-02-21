import socket
import os

logins_passwords = {}

def start_the_server():
    try:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #семья и тип сервера в скобках
        IP = '127.0.0.1' #socket.gethostbyname(socket.gethostname())
        PORT = 1233
        server.bind((IP, PORT)) 
        #server = socket.create_server((IP, PORT)) то же, что и выше - создание самого сервера
        server.listen(4) #кол-во принимаемых запросов для режима ожидания

        print('Start working...')
        
        while True:
            client, address = server.accept() #принятие запроса с разделением на клиента и его адрес, ждем сигнала.
            data = client.recv(1024).decode('utf8')

            print(data, "\n\n\n\n")
            
            content = process_the_request(data)
            if content == 'SHUTDOWN':
                client.send(('Shutdown...').encode('utf'))
                server.shutdown(socket.SHUT_RDWR)
                server.close()
                return
            client.send(content.encode('utf8'))
            #сlient.shutdown(socket.SHUT_WR)
    except KeyboardInterrupt:
        server.close()
        print('\nShutdown...')


def process_the_request(request_data):
    request = request_data.split(' ')
    match request[0]:
        case 'shutdown':
                return 'SHUTDOWN'
        case 'Check_is_login_free' :
            if logins_passwords.get(request[1]) == None:
                return 'YES'
            else:
                return 'NO'
        case 'Set_login_and_password':
            logins_passwords[request[1]] = request[2]
            return 'Done'
        case _:
            return 'Error'


start_the_server()