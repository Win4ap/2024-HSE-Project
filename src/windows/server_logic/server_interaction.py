import requests
import os
import logging
from rsa import encrypt

from windows.server_logic.constants import IP, PORT, pubkey

URL = f'http://{IP}:{PORT}'

class ServerLogic():
    # TODO add more cases
    def check_status(self, answer):
        logging.info(f'Server answer: {answer.status_code} {answer.text}')
        if answer.status_code == 200:
            if answer.text[0] == '[' or answer.text[0] == '{':
                answer = answer.json()
            else:
                answer = (answer.text).replace('"', '')
            return answer
        elif answer.status_code == 404 or answer.status_code == 403 or answer.status_code == 423:
            answer = answer.json()
            return answer['detail']

    def get_login(self) -> list:
        path_to_login = os.path.join(os.getcwd(), 'src', 'windows', 'server_logic', 'state_login')
        with open(path_to_login, 'r') as file:
            data = (file.read()).split(' ')
        return data
    
    def auth_reg_request(self, state, command, login, password):
        password = password.encode('utf-8')
        password = encrypt(password, pubkey)
        logging.info(f'{command}: {state} {login}')
        try:
            if command == 'login':
                answer = requests.get(f'{URL}/{command}', data={'state': f'{state}', 'login': f'{login}'}, files={'password': password})
            elif command == 'register':
                answer = requests.post(f'{URL}/{command}', data={'state': f'{state}', 'login': f'{login}'}, files={'password': password})
            else:
                return 'FATAL'
        except requests.exceptions.ConnectionError:
            logging.info('Server is down')
            return 'server_error'
        return self.check_status(answer)
    
    def get_client_data(self, info):
        data = self.get_login()
        if data != []: state, login = data[0], data[1]
        else: return 'ты че натворил'
        logging.info(f'get_user_{info}: {state} {login}')
        try:
            answer = requests.get(f'{URL}/get_user_{info}', json={'state': f'{state}', 'login': f'{login}'})
        except requests.exceptions.ConnectionError:
            logging.info('Server is down')
            return 'server_error'
        return self.check_status(answer)
    
    def get_free_orders(self):
        data = self.get_login()
        if data != []: state, login = data[0], data[1]
        else: return 'ты че натворил'
        logging.info(f'get_free_orders: {state} {login}')
        try:
            answer = requests.get(f'{URL}/get_free_orders', json={'state': f'{state}', 'login': f'{login}'})
        except requests.exceptions.ConnectionError:
            logging.info('Server is down')
            return 'server_error'
        return self.check_status(answer)
    
    def get_delivery_orders(self):
        data = self.get_login()
        if data != []: state, login = data[0], data[1]
        else: return 'ты че натворил'
        logging.info(f'get_delivery_active_orders: {state} {login}')
        try:
            answer = requests.get(f'{URL}/get_active_orders', json={'state': f'{state}', 'login': f'{login}'})
        except requests.exceptions.ConnectionError:
            logging.info('Server is down')
            return 'server_error'
        return self.check_status(answer)
    
    def get_in_process_orders(self):
        data = self.get_login()
        if data != []: state, login = data[0], data[1]
        else: return 'ты че натворил'
        logging.info(f'get_in_process_orders: {state} {login}')
        try:
            answer = requests.get(f'{URL}/get_in_process_orders', json={'state': f'{state}', 'login': f'{login}'})
        except requests.exceptions.ConnectionError:
            logging.info('Server is down')
            return 'server_error'
        return self.check_status(answer)
    
    def get_auction_orders(self):
        data = self.get_login()
        if data != []: state, login = data[0], data[1]
        else: return 'ты че натворил'
        logging.info(f'get_auction_orders: {state} {login}')
        try:
            answer = requests.get(f'{URL}/get_auction_orders', json={'state': f'{state}', 'login': f'{login}'})
        except requests.exceptions.ConnectionError:
            logging.info('Server is down')
            return 'server_error'
        return self.check_status(answer)
    
    def get_profile_fullness(self):
        data = self.get_login()
        if data != []: state, login = data[0], data[1]
        else: return 'ты че натворил'
        logging.info(f'get_profile_fullness: {state} {login}')
        try:
            answer = requests.get(f'{URL}/get_profile_fullness', json={'state': f'{state}', 'login': f'{login}'})
        except requests.exceptions.ConnectionError:
            logging.info('Server is down')
            return 'server_error'
        return self.check_status(answer)
    
    def edit_profile(self, firstname, lastname, phone, path_to_avatar, path_to_passport):
        data = self.get_login()
        if data != []: state, login = data[0], data[1]
        else: return 'ты че натворил'
        logging.info(f'edit_profile: {state} {login} {firstname} {lastname} {phone} {path_to_avatar} {path_to_passport}')
        try:
            answer = requests.post(f'{URL}/upload_user_info', data={'state': f'{state}', 'login': f'{login}', 'name': f'{firstname}', 'surname': f'{lastname}', 'phone': f'{phone}'}, files={'profile_picture': open(path_to_avatar, mode = 'rb'), 'passport': open(path_to_passport, mode = 'rb')})
        except requests.exceptions.ConnectionError:
            logging.info('Server is down')
            return 'server_error'
        return self.check_status(answer)
    
    def get_profile_data(self):
        data = self.get_login()
        if data != []: state, login = data[0], data[1]
        else: return 'ты че натворил'
        logging.info(f'get_profile: {state} {login}')
        try:
            if self.get_profile_fullness() == 'false':
                return 'Not Found'
            path = os.path.join(os.getcwd(), 'src', 'windows', 'profile', 'avatar.jpg')
            answer = requests.get(f'{URL}/get_user_picture/profile_picture',  json={'state': f'{state}', 'login': f'{login}'})
            if answer.status_code == 200:
                with open(path, mode='wb') as file:
                    file.write(answer.content)
                answer = requests.get(f'{URL}/get_user_info', json={'state': f'{state}', 'login': f'{login}'})
        except requests.exceptions.ConnectionError:
            logging.info('Server is down')
            return 'server_error'
        return self.check_status(answer)
    
    def new_object(self, object, name, price, description, adress_from, adress_to, time, fee):
        data = self.get_login()
        if data != []: login = data[1]
        else: return 'ты че натворил'
        logging.info(f'new_object: {object} {name} {price} {description} {adress_from} {adress_to}')
        try:
            if object == 'template':
                answer = requests.post(f'{URL}/new_template', json={'owner': f'{login}', 'name': f'{name}', 'cost': f'{price}', 'description': f'{description}', 'start': f'{adress_from}', 'finish': f'{adress_to}', 'time': f'{time}', 'fee': f'{fee}'})
            else:
                print(f'{URL}/new_order/{object}')
                answer = requests.post(f'{URL}/new_order/{object}', json={'owner': f'{login}', 'name': f'{name}', 'cost': f'{price}', 'description': f'{description}', 'start': f'{adress_from}', 'finish': f'{adress_to}', 'time': f'{time}', 'fee': f'{fee}'})
        except requests.exceptions.ConnectionError:
            logging.info('Server is down')
            return 'server_error'
        return self.check_status(answer)
    
    def order_operation(self, operation, type, order_id): # operation = take/complete/delete
        data = self.get_login()
        if data != []: state, login = data[0], data[1]
        else: return 'ты че натворил'
        logging.info(f'{operation}_order: {state} {login}')
        type = type.rsplit('_orders', 1)[0]
        try:
            if operation == 'delete':
                answer = requests.delete(f'{URL}/{operation}_order/{type}/{order_id}', json={'state': f'{state}', 'login': f'{login}'})
            elif operation == 'take':
                answer = requests.put(f'{URL}/{operation}_order/{type}/{order_id}', json={'state': f'{state}', 'login': f'{login}'})
            else:
                answer = requests.put(f'{URL}/{operation}_order/{order_id}', json={'state': f'{state}', 'login': f'{login}'})
        except requests.exceptions.ConnectionError:
            logging.info('Server is down')
            return 'server_error'
        return self.check_status(answer)
    
    def get_archive_orders(self):
        data = self.get_login()
        if data != []: state, login = data[0], data[1]
        else: return 'ты че натворил'
        logging.info(f'get_archive: {state} {login}')
        try:
            answer = requests.get(f'{URL}/get_archive_orders', json={'state': f'{state}', 'login': f'{login}'})
        except requests.exceptions.ConnectionError:
            logging.info('Server is down')
            return 'server_error'
        return self.check_status(answer)
    
    def get_rating(self):
        data = self.get_login()
        if data != []: state, login = data[0], data[1]
        else: return 'ты че натворил'
        logging.info(f'get_rating: {state} {login}')
        try:
            answer = requests.get(f'{URL}/get_user_rating', json={'state': f'{state}', 'login': f'{login}'})
        except requests.exceptions.ConnectionError:
            logging.info('Server is down')
            return 'server_error'
        return self.check_status(answer)
    
    def rate_order(self, order_id, num):
        logging.info(f'rate_order: {order_id} {num}')
        try:
            answer = requests.put(f'{URL}/rate_order/{order_id}', data={'rating': num})
        except requests.exceptions.ConnectionError:
            logging.info('Server is down')
            return 'server_error'
        return self.check_status(answer)