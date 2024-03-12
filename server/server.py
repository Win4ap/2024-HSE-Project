import socket
import os
import logging
import sqlite3
import constants

path_to_database = os.path.join(
    os.getcwd(), 'database', 'database.db')


def start_the_server():
    logging.basicConfig(level=logging.DEBUG, filename="loggings.log",
                        filemode="w", format="%(asctime)s %(levelname)s %(message)s")
    with sqlite3.connect(path_to_database) as database:
        cursor = database.cursor()
        query = """ CREATE TABLE IF NOT EXISTS client_logins_passwords ( login TEXT, password TEXT ) """
        cursor.execute(query)
        query = """ CREATE TABLE IF NOT EXISTS delivery_logins_passwords ( login TEXT, password TEXT ) """
        cursor.execute(query)
        query = """ CREATE TABLE IF NOT EXISTS orders_list ( id INTEGER, login TEXT, name TEXT, cost INTEGER, description TEXT ) """
        cursor.execute(query)
        query = """ CREATE TABLE IF NOT EXISTS templates_list ( login TEXT, name TEXT, cost INTEGER, description TEXT ) """
        cursor.execute(query)
        database.commit()
    try:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        IP = constants.IP
        PORT = constants.PORT
        server.bind((IP, PORT))
        server.listen(10)
        logging.debug('Server has started!')
        while True:
            # принятие запроса с разделением на клиента и его адрес, ждем сигнала.
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
                    login = request[2]
                    name_of_order = request[3]
                    cost = int(request[4])
                    description = request[5]
                    return make_new_order(login, name_of_order, cost, description)
                case 'new_template':
                    logging.debug('client new_template case')
                    login = request[2]
                    name_of_template = request[3]
                    cost = int(request[4])
                    description = request[5]
                    return make_new_template(login, name_of_template, cost, description)
                case 'get_user_orders':
                    logging.debug('client get_user_orders case')
                    login = request[2]
                    return get_user_data(login, 'orders')
                case 'get_user_templates':
                    logging.debug('client get_user_templates case')
                    login = request[2]
                    return get_user_data(login, 'templates')
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
                case _:
                    return 'error error_of_request'
        case _:
            return 'error error_of_state'


def try_to_register(login, password, state) -> str:
    logging.debug('try to register')
    with sqlite3.connect(path_to_database) as database:
        logging.debug('connected to database')
        cursor = database.cursor()
        query = f""" SELECT login FROM {state}_logins_passwords WHERE login = ? """
        cursor.execute(query, (login,))
        user = cursor.fetchone()
        if user == None:
            query = f""" INSERT INTO {state}_logins_passwords (login, password) VALUES (?, ?) """
            cursor.execute(query, (login, password))
            database.commit()
            return 'done'
        else:
            return 'error login_exists'


def try_to_login(login, password, state) -> str:
    logging.debug('try to login')
    with sqlite3.connect(path_to_database) as database:
        logging.debug('connected to database')
        cursor = database.cursor()
        query = f""" SELECT * FROM {state}_logins_passwords WHERE login = ? """
        cursor.execute(query, (login,))
        user = cursor.fetchone()
        if user == None:
            return 'error login_doesnt_exists'
        else:
            if password == user[1]:
                return 'done correct ' + state + ' ' + login
            else:
                return 'done incorrect'


def make_new_order(login, name, cost, description) -> str:
    logging.debug('make new order')
    cur_id = -1
    with sqlite3.connect(path_to_database) as database:
        logging.debug('connected to database')
        cursor = database.cursor()
        query = """ SELECT login FROM client_logins_passwords WHERE login = ? """
        cursor.execute(query, (login,))
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
        query = """ INSERT INTO orders_list (id, login, name, cost, description) VALUES (?, ?, ?, ?, ?) """
        cursor.execute(query, (cur_id, login, name, cost, description))
        database.commit()
    return f"done {cur_id}"


def make_new_template(login, name, cost, description) -> str:
    logging.debug('make new template')
    with sqlite3.connect(path_to_database) as database:
        logging.debug('connected to database')
        cursor = database.cursor()
        query = """ SELECT login FROM client_logins_passwords WHERE login = ? """
        cursor.execute(query, (login,))
        if cursor.fetchone() == None:
            return 'error login_doesnt_exists'
        query = """ INSERT INTO templates_list (login, name, cost, description) VALUES (?, ?, ?, ?) """
        cursor.execute(query, (login, name, cost, description))
        database.commit()
    return 'done'


def get_user_data(login, data) -> str:
    logging.debug(f"get user's {data}")
    result = 'done '
    with sqlite3.connect(path_to_database) as database:
        logging.debug('connected to database')
        cursor = database.cursor()
        query = """ SELECT login FROM client_logins_passwords WHERE login = ? """
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


start_the_server()
