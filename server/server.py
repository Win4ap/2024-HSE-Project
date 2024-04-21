from fastapi import FastAPI, UploadFile
from fastapi.responses import FileResponse
import uvicorn
import os
import logging
import sqlite3
from AdditionalClasses import Order 


path_to_database = os.path.join(
    os.getcwd(), '2024-HSE-Project', 'server', 'database', 'database.db')
server = FastAPI()


@server.post('/register')
def try_to_register(body: str) -> str:
    logging.info('try to register')
    body = body.split('~')
    state = body[0]
    login = body[1]
    password = body[2]
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


@server.get('/login')
def try_to_login(body: str) -> str:
    logging.info('try to login')
    body = body.split('~')
    state = body[0]
    login = body[1]
    password = body[2]
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


@server.post('/new_order')
def make_new_order(body: str) -> str:
    logging.info('make new order')
    body = body.split('~')
    order = Order(body[0], body[1], int(body[2]), body[3], body[4], body[5])
    logging.debug('splited')
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
        if right == 0 or order_id[0][0] != 0:
            cur_id = 0
        elif right == 0 or right == order_id[-1][0] + 1:
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


@server.post('/new_template')
def make_new_template(body: str) -> str:
    body = body.split('~')
    order = Order(body[0], body[1], int(body[2]), body[3], body[4], body[5])
    logging.info('make new template')
    with sqlite3.connect(path_to_database) as database:
        logging.debug('connected to database')
        cursor = database.cursor()
        query = """ SELECT login FROM client_data WHERE login = ? """
        cursor.execute(query, (order.owner,))
        if cursor.fetchone() == None:
            return 'error login_doesnt_exists'
        query = """ INSERT INTO templates_list (login, name, cost, description, start, finish, supplier) VALUES (?, ?, ?, ?, ?, ?, ?) """
        cursor.execute(query, order.get_tuple())
        database.commit()
    return 'done'


@server.get('/get_profile_fullness')
def get_profile_fullness(body: str) -> str:
    body = body.split('~')
    state = body[0]
    login = body[1]
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


@server.get('/get_user_{data}') #getting orders or templates
def get_user_data(data, login) -> str:
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


# @server.put('/edit_profile')
# def edit_profile(state: str, login: str, name: str, surname: str, phone: str, profile_picture: UploadFile, passport: UploadFile) -> str:
#     logging.info(
#         f'{state} {login} editing profile with a data: ' +
#         f'name = {name}, surname = {surname}, phone = {phone}')
#     result = 'done '
#     path_to_profile_picture = os.path.join(
#         os.getcwd(), '2024-HSE-Project', 'server', 'images', f'{state}_{login}_profile_picture.jpg')
#     with open(path_to_profile_picture, mode='wb') as file:
#         file.write(profile_picture)
#     logging.debug('Done with profile picture')
#     path_to_passport = os.path.join(
#         os.getcwd(), '2024-HSE-Project', 'server', 'images', f'{state}_{login}_passport.jpg')
#     logging.debug('Try to get size of passport image')
#     with open(path_to_passport, mode='wb') as file:
#         file.write(passport)
#     logging.debug('Done with passport picture')
#     with sqlite3.connect(path_to_database) as database:
#         logging.debug('connected to database')
#         cursor = database.cursor()
#         query = f""" UPDATE {state}_data SET name = ?, surname = ?, phone = ?, fullness = ? WHERE login = ?"""
#         cursor.execute(query, (name, surname, phone, 1, login))
#         database.commit()
#     return result


@server.get('/get_user_picture/{picture}')
def get_user_file(picture, state: str, login: str) -> bytes: #getting user's passport or picture
    logging.info(f'Get profile picture of {state} {login}')
    with sqlite3.connect(path_to_database) as database:
        logging.debug('connected to database')
        cursor = database.cursor()
        query = f""" SELECT fullness FROM {state}_data WHERE login = ? """
        cursor.execute(query, (login,))
        user = cursor.fetchone()
        if user == None or user[0] == 0:
            raise HTTPException(status_code=404, detail="Item not found")
    path_to_picture = os.path.join(
        os.getcwd(), '2024-HSE-Project', 'server', 'images', f'{state}_{login}_{picture}.jpg')
    return FileResponse(path=path_to_picture)


logging.basicConfig(level=logging.INFO, filename="loggings.log",
                    filemode="w", format="%(asctime)s %(levelname)s %(message)s")
with sqlite3.connect(path_to_database) as database:
    cursor = database.cursor()
    query = """ CREATE TABLE IF NOT EXISTS client_data ( login TEXT, password TEXT, name TEXT, surname TEXT, phone TEXT, fullness INTEGER ) """
    cursor.execute(query)
    query = """ CREATE TABLE IF NOT EXISTS delivery_data ( login TEXT, password TEXT, name TEXT, surname TEXT, phone TEXT, fullness INTEGER ) """
    cursor.execute(query)
    query = """ CREATE TABLE IF NOT EXISTS orders_list ( id INTEGER, login TEXT, name TEXT, cost INTEGER, description TEXT, start TEXT, finish TEXT, supplier TEXT ) """
    cursor.execute(query)
    query = """ CREATE TABLE IF NOT EXISTS templates_list ( login TEXT, name TEXT, cost INTEGER, description TEXT, start TEXT, finish TEXT, supplier TEXT ) """
    cursor.execute(query)
    database.commit()

uvicorn.run(server, host = '127.0.0.1', port = 1233)