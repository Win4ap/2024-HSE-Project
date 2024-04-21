import socket
import requests
import os
import logging
import sys 
sys.set_int_max_str_digits(1000000000)
from windows.server_logic.constants import IP, PORT
from windows.server_logic.raw_rsa import RSA

URL = f'http://{IP}:{PORT}'

class ServerLogic():
    def get_login(self) -> list:
        path_to_login = os.path.join(os.getcwd(), 'src', 'windows', 'server_logic', 'state_login')
        with open(path_to_login, 'r') as file:
            data = (file.read()).split(' ')
        return data

    # TODO register -> fastAPI
    def auth_reg_request(self, state, command, login, password) -> str:
        password = RSA().encrypt(password)
        logging.info(f'{command}: {state} {login}')
        if command == 'login':
            answer = requests.get(f'{URL}/{command}', {'body': f'{state}~{login}~{password}'})
        #else:
        #    answer = requests.post(f'{URL}/{command}', {'body': f'{state}~{login}~{password}'})
        if answer.status_code == 200:
            answer = (answer.text).replace('"', '')
            logging.info(f'Server answer: {answer}')
            return answer
        else:
            logging.info('Server is down')
            return 'server_error'
    
    # TODO -> fastAPI
    def get_client_data(self, info) -> str:
        data = self.get_login()
        if data != []: state, login = data[0], data[1]
        else: return 'ты че натворил'
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
    
    # TODO -> fastAPI
    def get_profile_fullness(self) -> str:
        data = self.get_login()
        if data != []: state, login = data[0], data[1]
        else: return 'ты че натворил'
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
    
    # TODO -> fastAPI
    def edit_profile(self, firstname, lastname, phone, path_to_avatar, path_to_passport) -> str:
        data = self.get_login()
        if data != []: state, login = data[0], data[1]
        else: return 'ты че натворил'
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
    
    # TODO -> fastAPI
    def get_profile_data(self) -> str:
        data = self.get_login()
        if data != []: state, login = data[0], data[1]
        else: return 'ты че натворил'
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
            try:
                client.connect((IP, PORT))
                request = f'{state} get_profile_info {login}'
                client.send(request.encode('utf8'))
                size = client.recv(1024).decode('utf8')
                if size[:5] == 'error':
                    return size
                else:
                    size = int(size)
                client.send(f'debug size_is_{size}'.encode('utf8'))
                path = os.path.join(os.getcwd(), 'src', 'windows', 'profile', 'avatar.jpg')
                processed_size = 0
                with open(path, mode='wb') as file:
                    while processed_size < size:
                        data = client.recv(2048)
                        processed_size += len(data)
                        file.write(data)
                client.send(('debug done').encode('utf8'))
                answer = client.recv(1024).decode('utf8')
            except ConnectionRefusedError:
                logging.info('Server is down')
                answer = 'server_error'
        return answer
    
    # TODO -> fastAPI
    def new_object(self, object, name, price, description, adress_from, adress_to):
        data = self.get_login()
        if data != []: state, login = data[0], data[1]
        else: return 'ты че натворил'
        request = f'{state} new_{object} {login} {name} {price} {description} {adress_from} {adress_to}'
        logging.info(f'new_object: {object} {name} {price} {description} {adress_from} {adress_to}')
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