import socket
import os
import logging
import sqlite3
import constants
from AdditionalClasses import Order 


path_to_database = os.path.join(
    os.getcwd(), 'database', 'database.db')


def start_the_server():
    logging.basicConfig(level=logging.INFO, filename="loggings.log",
                        filemode="w", format="%(asctime)s %(levelname)s %(message)s")
    with sqlite3.connect(path_to_database) as database:
        cursor = database.cursor()
        query = """ CREATE TABLE IF NOT EXISTS client_data ( login TEXT, password TEXT, name TEXT, surname TEXT, phone_number TEXT, fullness INTEGER ) """
        cursor.execute(query)
        query = """ CREATE TABLE IF NOT EXISTS delivery_data ( login TEXT, password TEXT, name TEXT, surname TEXT, phone_number TEXT, fullness INTEGER ) """
        cursor.execute(query)
        query = """ CREATE TABLE IF NOT EXISTS orders_list ( id INTEGER, login TEXT, name TEXT, cost INTEGER, description TEXT, start TEXT, finish TEXT, supplier TEXT ) """
        cursor.execute(query)
        query = """ CREATE TABLE IF NOT EXISTS templates_list ( login TEXT, name TEXT, cost INTEGER, description TEXT, start TEXT, finish TEXT, supplier TEXT ) """
        cursor.execute(query)
        database.commit()
    try:
        global server
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        IP = constants.IP
        PORT = constants.PORT
        server.bind((IP, PORT))
        server.listen()
        logging.info('Server has started!')
        while True:
            # принятие запроса с разделением на клиента и его адрес, ждем сигнала.
            global client
            client, address = server.accept()
            data = client.recv(1024).decode('utf8')
            logging.info('Some data have received:\n\n' + data + '\n')
            content = process_the_request(data)
            logging.info('Answer for the request is\n\n' + content + '\n')
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
                    logging.debug('client register case')
                    login = request[2]
                    password_input = request[3]
                    return try_to_register(login, password_input, state)
                case 'login':
                    logging.debug('client login case')
                    login = request[2]
                    password_input = request[3]
                    return try_to_login(login, password_input, state)
                case 'new_order':
                    logging.debug('client new_order case')
                    order = Order(request[2], request[3], int(request[4]), request[5], request[6], request[7])
                    return make_new_order(order)
                case 'new_template':
                    logging.debug('client new_template case')
                    order = Order(request[2], request[3], int(request[4]), request[5], request[6], request[7])
                    return make_new_template(order)
                case 'get_user_orders':
                    logging.debug('client get_user_orders case')
                    login = request[2]
                    return get_user_data(login, 'orders')
                case 'get_user_templates':
                    logging.debug('client get_user_templates case')
                    login = request[2]
                    return get_user_data(login, 'templates')
                case 'get_profile_fullness':
                    logging.debug('client get_profile_fullness case')
                    login = request[2]
                    return get_profile_fullness(login, state)
                case 'edit_profile':
                    login = request[2]
                    name = request[3]
                    surname = request[4]
                    phone = request[5]
                    return edit_profile(state, login, name, surname, phone)
                case _:
                    return 'error error_of_request'
        case 'delivery':
            match request[1]:
                case 'register':
                    logging.debug('delivery register case')
                    login = request[2]
                    password_input = request[3]
                    return try_to_register(login, password_input, state)
                case 'login':
                    logging.debug('delivery login case')
                    login = request[2]
                    password_input = request[3]
                    return try_to_login(login, password_input, state)
                case 'get_profile_fullness':
                    logging.debug('client get_profile_fullness case')
                    login = request[2]
                    return get_profile_fullness(login, state)
                case _:
                    return 'error error_of_request'
        case _:
            return 'error error_of_state'


def try_to_register(login, password, state) -> str:
    logging.info('try to register')
    with sqlite3.connect(path_to_database) as database:
        logging.debug('connected to database')
        cursor = database.cursor()
        query = f""" SELECT login FROM {state}_data WHERE login = ? """
        cursor.execute(query, (login,))
        user = cursor.fetchone()
        if user == None:
            query = f""" INSERT INTO {state}_data (login, password, fullness) VALUES (?, ?, ?) """
            cursor.execute(query, (login, password, 0))
            database.commit()
            return 'done'
        else:
            return 'error login_exists'


def try_to_login(login, password, state) -> str:
    logging.info('try to login')
    with sqlite3.connect(path_to_database) as database:
        logging.debug('connected to database')
        cursor = database.cursor()
        query = f""" SELECT * FROM {state}_data WHERE login = ? """
        cursor.execute(query, (login,))
        user = cursor.fetchone()
        if user == None:
            return 'error login_doesnt_exists'
        else:
            if password == user[1]:
                return 'done correct ' + state + ' ' + login
            else:
                return 'done incorrect'


def make_new_order(order) -> str:
    logging.info('make new order')
    cur_id = -1
    with sqlite3.connect(path_to_database) as database:
        logging.debug('connected to database')
        cursor = database.cursor()
        query = """ SELECT login FROM client_data WHERE login = ? """
        cursor.execute(query, (order.owner,))
        if cursor.fetchone() == None:
            return 'error login_doesnt_exists'
        query = """ SELECT id FROM orders_list ORDER BY id """
        cursor.execute(query)
        order_id = cursor.fetchall()
        left = 0
        right = len(order_id)
        if right == 0 or right == order_id[-1][0] + 1:
            cur_id = right
        else:
            while right - left > 1:
                mid = (right + left) // 2
                if order_id[mid][0] == mid:
                    left = mid 
                else:
                    right = mid 
            cur_id = right 
        query = """ INSERT INTO orders_list (id, login, name, cost, description, start, finish, supplier) VALUES (?, ?, ?, ?, ?, ?, ?, ?) """
        cursor.execute(query, (cur_id,) + order.get_tuple())
        database.commit()
    return f"done {cur_id}"


def make_new_template(order) -> str:
    logging.info('make new template')
    with sqlite3.connect(path_to_database) as database:
        logging.debug('connected to database')
        cursor = database.cursor()
        query = """ SELECT login FROM client_data WHERE login = ? """
        cursor.execute(query, (login,))
        if cursor.fetchone() == None:
            return 'error login_doesnt_exists'
        query = """ INSERT INTO templates_list (login, name, cost, description, start, finish, supplier) VALUES (?, ?, ?, ?, ?, ?, ?) """
        cursor.execute(query, order.get_tuple())
        database.commit()
    return 'done'


def get_user_data(login, data) -> str:
    logging.info(f"get user's {data}")
    result = 'done '
    with sqlite3.connect(path_to_database) as database:
        logging.debug('connected to database')
        cursor = database.cursor()
        query = """ SELECT login FROM client_data WHERE login = ? """
        cursor.execute(query, (login,))
        if cursor.fetchone() == None:
            return 'error login_doesnt_exists'
        query = f""" SELECT * FROM {data}_list WHERE login = ? """
        cursor.execute(query, (login,))
        data = cursor.fetchall()
        if data == None:
            return 'done not_found'
        for item in data:
            result += '~ '
            for elem in item:
                result += str(elem) + ' '
    return result


def get_profile_fullness(login, state) -> str:
    logging.info(f'getting profile fullness: {state} {login}')
    result = 'done '
    with sqlite3.connect(path_to_database) as database:
        logging.debug('connected to database')
        cursor = database.cursor()
        query = f""" SELECT login FROM {state}_data WHERE login = ? """
        cursor.execute(query, (login,))
        if cursor.fetchone() == None:
            return 'error login_doesnt_exists'
        query = f""" SELECT fullness FROM {state}_data WHERE login = ? """
        cursor.execute(query, (login,))
        fullness = cursor.fetchone()[0]
        if fullness:
            result += 'True'
        else:
            result += 'False'
    return result


def edit_profile(state, login, name, surname, phone) -> str:
    logging.info(
        f'{state} {login} editing profile with a data: ' + 
        f'name = {name}, surname = {surname}, phone = {phone}')
    result = 'done '
    path_to_profile_picture = os.path.join(
        os.getcwd(), 'images', f'{state}_{login}_profile_picture.jpg')
    size = int(client.recv(1024))
    client.send((f'debug size_is_{size}').encode('utf8'))
    logging.debug(f'Got size of picture: {size}')
    processed_size = 0
    with open(path_to_profile_picture, mode = 'wb') as profile_picture:
        while processed_size < size:
            data = client.recv(2048)
            profile_picture.write(data)
            processed_size += len(data)
            logging.debug(f'processed size if {processed_size} of {size}')
    logging.debug('Done with profile picture')
    client.send(('debug Done_with_profile_picture').encode('utf8'))
    path_to_passport = os.path.join(
        os.getcwd(), 'images', f'{state}_{login}_passport.jpg')
    logging.debug('Try to get size of passport image')
    size = int(client.recv(1024))
    client.send((f'debug size_is_{size}').encode('utf8'))
    logging.debug(f'Got size of passport: {size}')
    processed_size = 0
    with open(path_to_passport, mode = 'wb') as passport:
        while processed_size < size:
            data = client.recv(2048)
            passport.write(data)
            processed_size += len(data)
            logging.debug(f'processed size if {processed_size} of {size}')
    logging.debug('Done with passport picture')
    with sqlite3.connect(path_to_database) as database:
        logging.debug('connected to database')
        cursor = database.cursor()
        query = f""" UPDATE {state}_data SET name = ?, surname = ?, phone_number = ?, fullness = ? WHERE login = ?"""
        cursor.execute(query, (name, surname, phone, 1, login))
        database.commit()
    return result


start_the_server()
