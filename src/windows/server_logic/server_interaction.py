import socket
import os
import logging

class ServerLogic():
    constants = []
    try:
        path_to_constants = os.path.join(os.getcwd(), 'src', 'windows', 'server_logic', 'constants')
        with open(path_to_constants, 'r') as f:
            constants = (f.read()).split(' ')
    except FileNotFoundError:
        logging.error('Cannot found file with constants!')
    IP = constants[0]
    PORT = int(constants[1])

    def auth_reg_request(self, state, command, login, password) -> str:
        request = f'{state} {command} {login} {password}'
        logging.info(f'{command}: {state} {login}')
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
            try:
                client.connect((self.IP, self.PORT))
                client.send(request.encode('utf8'))
                answer = client.recv(1024).decode('utf8')
                logging.info(f'Server answer: {answer}')
            except ConnectionRefusedError:
                logging.info('Server is down')
                answer = 'server_error'
        return answer