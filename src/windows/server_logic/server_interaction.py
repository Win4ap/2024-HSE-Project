import socket
import os
import logging
from windows.server_logic.constants import IP, PORT

class ServerLogic():
    def auth_reg_request(self, state, command, login, password) -> str:
        request = f'{state} {command} {login} {password}'
        logging.info(f'{command}: {state} {login}')
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
            try:
                client.connect((IP, PORT))
                client.send(request.encode('utf8'))
                answer = client.recv(1024).decode('utf8')
                logging.info(f'Server answer: {answer}')
            except ConnectionRefusedError:
                logging.info('Server is down')
                answer = 'server_error'
        return answer
    
    def get_client_data(self, info) -> str:
        path_to_login = os.path.join(os.getcwd(), 'src', 'windows', 'server_logic', 'state_login')
        with open(path_to_login, 'r') as file:
            data = (file.read()).split(' ')
        state = data[0]
        login = data[1]
        request = f'{state} get_user_{info} {login}'
        logging.info(f'get_user_{info}: {state} {login}')
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
            try:
                client.connect((IP, PORT))
                client.send(request.encode('utf8'))
                answer = client.recv(1024).decode('utf8')
                logging.info(f'Server answer: {answer}')
            except ConnectionRefusedError:
                logging.info('Server is down')
                answer = 'server_error'
        return answer
    
    def get_profile_fullness(self) -> str:
        path_to_login = os.path.join(os.getcwd(), 'src', 'windows', 'server_logic', 'state_login')
        with open(path_to_login, 'r') as file:
            data = (file.read()).split(' ')
        state = data[0]
        login = data[1]
        request = f'{state} get_profile_fullness {login}'
        logging.info(f'get_profile_fullness: {state} {login}')
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
            try:
                client.connect((IP, PORT))
                client.send(request.encode('utf8'))
                answer = client.recv(1024).decode('utf8')
                logging.info(f'Server answer: {answer}')
            except ConnectionRefusedError:
                logging.info('Server is down')
                answer = 'server_error'
        return answer
    
    def edit_profile(self, firstname, lastname, phone, path_to_avatar, path_to_passport) -> str:
        path_to_login = os.path.join(os.getcwd(), 'src', 'windows', 'server_logic', 'state_login')
        with open(path_to_login, 'r') as file:
            data = (file.read()).split(' ')
        state = data[0]
        login = data[1]
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
            try:
                client.connect((IP, PORT))
                request = f'{state} edit_profile {login} {firstname} {lastname} {phone}'
                client.send(request.encode('utf8'))
                size = str(os.path.getsize(path_to_avatar))
                client.send(size.encode('utf8'))
                logging.info(client.recv(1024).decode('utf8'))
                with open(path_to_avatar, mode = 'rb') as file:
                    data = file.read(2048)
                    while data:
                        client.send(data)
                        data = file.read(2048)
                answer = client.recv(1024).decode('utf8')
                size = str(os.path.getsize(path_to_passport))
                client.send(size.encode('utf8'))
                with open(path_to_passport, mode = 'rb') as file:
                    data = file.read(2048)
                    while data:
                        client.send(data)
                        data = file.read(2048)
                answer = client.recv(1024).decode('utf8')
                client.close()
                logging.info(answer)
            except ConnectionRefusedError:
                logging.info('Server is down')
                answer = 'server_error'
        return answer