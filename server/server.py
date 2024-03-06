import socket
import os
import logging
import sqlite3


def start_the_server():
    logging.basicConfig(level=logging.DEBUG, filename="loggings.log",
                        filemode="w", format="%(asctime)s %(levelname)s %(message)s")
    path_to_database = os.path.join(
        os.getcwd(), 'database', 'database.db')
    with sqlite3.connect(path_to_database) as database:
        cursor = database.cursor()
        query = """ CREATE TABLE IF NOT EXISTS client_logins_passwords ( login TEXT, password TEXT ) """
        cursor.execute(query)
        query = """ CREATE TABLE IF NOT EXISTS delivery_logins_passwords ( login TEXT, password TEXT ) """
        cursor.execute(query)
        database.commit()
    try:
        path_to_constants = os.path.join(os.getcwd(), 'constants')
        with open(path_to_constants, 'r') as f:
            constants = (f.read()).split(' ')
    except FileNotFoundError:
        logging.error('Cannot found file with constants!')
    try:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        IP = constants[0]
        PORT = int(constants[1])
        server.bind((IP, PORT))
        server.listen(10)
        logging.debug('Server has started!')
        while True:
            # принятие запроса с разделением на клиента и его адрес, ждем сигнала.
            client, address = server.accept()
            data = client.recv(1024).decode('utf8')
            logging.info('Some data have received:\n\n' + data)
            content = process_the_request(data)
            client.send(content.encode('utf8'))
            client.shutdown(socket.SHUT_WR)
            client.close()
    except KeyboardInterrupt:
        logging.info('Server has shutdowned with KeybordInterrupt...')
    finally:
        server.close()
        return


def process_the_request(request_data):
    request = request_data.split(' ')
    state = request[0]
    match state:
        case 'client':
            match request[1]:
                case 'register':
                    login_input = request[2]
                    password_input = request[3]
                    return try_to_register(login_input, password_input, state)
                case 'login':
                    login_input = request[2]
                    password_input = request[3]
                    return try_to_login(login_input, password_input, state)
                case _:
                    return 'error_of_request'
        case 'delivery':
            match request[1]:
                case 'register':
                    login_input = request[2]
                    password_input = request[3]
                    return try_to_register(login_input, password_input, state)
                case 'login':
                    login_input = request[2]
                    password_input = request[3]
                    return try_to_login(login_input, password_input, state)
                case _:
                    return 'error_of_request'
        case _:
            return 'error_of_state'


def try_to_register(login, password, state) -> str:
    with sqlite3.connect(path_to_database) as database:
        cursor = database.cursor()
        query = f""" SELECT login FROM {state}
            _logins_passwords WHERE login = ? """
        cursor.execute(query, (login,))
        user = cursor.fetchone()
        if user == None:
            query = f""" INSERT INTO {
                state}_logins_passwords (login, password) VALUES (?, ?) """
            cursor.execute(query, (login, password))
            database.commit()
            return 'done_successfully'
        else:
            return 'login_exists'


def try_to_login(login, password, state) -> str:
    with sqlite3.connect(path_to_database) as database:
        cursor = database.cursor()
        query = f""" SELECT * FROM {state}_logins_passwords WHERE login = ? """
        cursor.execute(query, (login,))
        user_password = cursor.fetchone()[1]
        if user == None:
            return 'login_doesnt_exists'
        else:
            if password == user_password:
                return 'correct ' + state + ' ' + login
            else:
                return 'incorrect'


start_the_server()
