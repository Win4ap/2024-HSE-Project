import requests
import os
import logging

from windows.server_logic.constants import IP, PORT
from windows.server_logic.raw_rsa import RSA

URL = f'http://{IP}:{PORT}'

class ServerLogic():
    # TODO add more
    def check_status(self, answer):
        logging.info(f'Server answer: {answer.status_code}, {answer.text}')
        if answer.status_code == 200:
            answer = (answer.text).replace('"', '')
            return answer
        elif answer.status_code == 404:
            answer = answer.json()
            return answer['detail']
        else:
            logging.info('Server is down')
            return 'server_error'

    def get_login(self) -> list:
        path_to_login = os.path.join(os.getcwd(), 'src', 'windows', 'server_logic', 'state_login')
        with open(path_to_login, 'r') as file:
            data = (file.read()).split(' ')
        return data
    
    def auth_reg_request(self, state, command, login, password) -> str:
        password = RSA().encrypt(password)
        logging.info(f'{command}: {state} {login}')
        if command == 'login':
            answer = requests.get(f'{URL}/{command}', json={'state': f'{state}', 'login': f'{login}', 'password': f'{password}'})
        elif command == 'register':
            answer = requests.post(f'{URL}/{command}', json={'state': f'{state}', 'login': f'{login}', 'password': f'{password}'})
        else:
            return 'FATAL'
        return self.check_status(answer)
    
    def get_client_data(self, info) -> str:
        data = self.get_login()
        if data != []: state, login = data[0], data[1]
        else: return 'ты че натворил'
        logging.info(f'get_user_{info}: {state} {login}')
        answer = requests.get(f'{URL}/get_user_{info}', json={'state': f'{state}', 'login': f'{login}'})
        return self.check_status(answer)
    
    def get_profile_fullness(self) -> str:
        data = self.get_login()
        if data != []: state, login = data[0], data[1]
        else: return 'ты че натворил'
        logging.info(f'get_profile_fullness: {state} {login}')
        answer = requests.get(f'{URL}/get_profile_fullness', json={'state': f'{state}', 'login': f'{login}'})
        return self.check_status(answer)
    
    def edit_profile(self, firstname, lastname, phone, path_to_avatar, path_to_passport) -> str:
        data = self.get_login()
        if data != []: state, login = data[0], data[1]
        else: return 'ты че натворил'
        answer = requests.post(f'{URL}/upload_user_info', json={'state': f'{state}', 'login': f'{login}', 'name': f'{firstname}', 'surname': f'{lastname}', 'phone': f'{phone}'}, files={'profile_picture': open(path_to_avatar, mode = 'rb'), 'passport': open(path_to_passport, mode = 'rb')})
        return self.check_status(answer)
    
    def get_profile_data(self) -> str:
        data = self.get_login()
        if data != []: state, login = data[0], data[1]
        else: return 'ты че натворил'
        if self.get_profile_fullness() == 'false':
            return 'Not Found'
        path = os.path.join(os.getcwd(), 'src', 'windows', 'profile', 'avatar.jpg')
        answer = requests.get(f'{URL}/get_user_picture/profile_picture',  json={'state': f'{state}', 'login': f'{login}'})
        if answer.status_code == 200:
            with open(path, mode='wb') as file:
                file.write(answer.content)
            answer = requests.get(f'{URL}/get_user_info', json={'state': f'{state}', 'login': f'{login}'})
        return self.check_status(answer)
    
    def new_object(self, object, name, price, description, adress_from, adress_to):
        data = self.get_login()
        if data != []: state, login = data[0], data[1]
        else: return 'ты че натворил'
        logging.info(f'new_object: {object} {name} {price} {description} {adress_from} {adress_to}')
        answer = requests.post(f'{URL}/new_{object}', json={'owner': f'{login}', 'name': f'{name}', 'cost': f'{price}', 'description': f'{description}', 'start': f'{adress_from}', 'finish': f'{adress_to}'})
        return self.check_status(answer)