import socket
import os

client_logins_passwords = {}
delivery_logins_passwords = {}

def start_the_server():
    try:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        IP = '127.0.0.1' 
        PORT = 1233
        server.bind((IP, PORT)) 
        server.listen(4) 

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
    except KeyboardInterrupt:
        server.close()
        print('\nShutdown...')


def process_the_request(request_data):
    request = request_data.split(' ')
    match request[0]:
        case 'shutdown':
                return 'SHUTDOWN'
        case 'register':
            state = request[1]
            login_input = request[2]
            password_input = request[3]
            if state == 'client':
                if client_logins_passwords.get(login_input) != None:
                    return 'login_exists'
                client_logins_passwords[login_input] = password_input
                return 'done_successfully'
            if state == 'delivery':
                if delivery_logins_passwords.get(login_input) != None:
                    return 'login_exists'
                delivery_logins_passwords[login_input] = password_input
                return 'done_successfully'
            return 'Error'
        case 'login':
            state = request[1]
            login_input = request[2]
            password_input = request[3]
            if state == 'client':
                if client_logins_passwords.get(login_input) == None:
                    return 'login_doesnt_exists'
                if client_logins_passwords[login_input] == password_input:
                    return 'correct'
                else:
                    return 'incorrect'
            if state == 'delivery':
                if delivery_logins_passwords.get(login_input) == None:
                    return 'login_doesnt_exists'
                if delivery_logins_passwords[login_input] == password_input:
                    return 'correct'
                else:
                    return 'incorrect'
            return 'Error'
        case _:
            return 'Error'


start_the_server()
