from fastapi import FastAPI, HTTPException, UploadFile
from fastapi.responses import FileResponse
from fastapi.logger import logger
from pydantic import BaseModel
from AdditionalClasses import Order, User 
import uvicorn
import os
import logging
import sqlite3
import constants


path_to_database = os.path.join(
    os.getcwd(), 'database', 'database.db')
server = FastAPI()


@server.post('/register')
def try_to_register(user: User) -> str:
    logging.info('try to register')
    with sqlite3.connect(path_to_database) as database:
        logging.debug('connected to database')
        cursor = database.cursor()
        query = f""" SELECT login FROM {user.state}_data WHERE login = ? """
        cursor.execute(query, (user.login,))
        user = cursor.fetchone()
        if user == None:
            query = f""" INSERT INTO {user.state}_data (login, password, fullness) VALUES (?, ?, ?) """
            cursor.execute(query, (user.login, user.password, 0))
            database.commit()
            return 'done'
        else:
            raise HTTPException(status_code=423, detail='Login already in use')


@server.get('/login')
def try_to_login(user: User) -> str:
    logging.info('try to login')
    with sqlite3.connect(path_to_database) as database:
        logging.debug('connected to database')
        cursor = database.cursor()
        query = f""" SELECT * FROM {user.state}_data WHERE login = ? """
        cursor.execute(query, (user.login,))
        data = cursor.fetchone()
        if data == None:
            raise HTTPException(status_code=404, detail="Item not found")
        else:
            if user.password == data[1]:
                return 'done correct ' + user.state + ' ' + user.login
            else:
                return 'done incorrect'


@server.post('/new_order')
def make_new_order(order: Order) -> str:
    logging.info('make new order')
    cur_id = -1
    with sqlite3.connect(path_to_database) as database:
        logging.debug('connected to database')
        cursor = database.cursor()
        query = """ SELECT login FROM client_data WHERE login = ? """
        cursor.execute(query, (order.owner,))
        if cursor.fetchone() == None:
            raise HTTPException(status_code=404, detail="Item not found")
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
def make_new_template(order: Order) -> str:
    logging.info('make new template')
    with sqlite3.connect(path_to_database) as database:
        logging.debug('connected to database')
        cursor = database.cursor()
        query = """ SELECT login FROM client_data WHERE login = ? """
        cursor.execute(query, (order.owner,))
        if cursor.fetchone() == None:
            raise HTTPException(status_code=404, detail="Item not found")
        query = """ INSERT INTO templates_list (login, name, cost, description, start, finish, supplier) VALUES (?, ?, ?, ?, ?, ?, ?) """
        cursor.execute(query, order.get_tuple())
        database.commit()
    return 'done'


@server.get('/get_profile_fullness')
def get_profile_fullness(user: User) -> bool:
    logging.info(f'getting profile fullness: {user.state} {user.login}')
    result = True
    with sqlite3.connect(path_to_database) as database:
        logging.debug('connected to database')
        cursor = database.cursor()
        query = f""" SELECT fullness FROM {user.state}_data WHERE login = ? """
        cursor.execute(query, (user.login,))
        data = cursor.fetchone()
        if data == None:
            raise HTTPException(status_code=404, detail="Item not found")
        result = data[0]
    return result


@server.get('/get_user_info')
def get_user_info(user: User) -> str:
    logging.info(f'Get main info of {user.state} {user.login}')
    result = ''
    with sqlite3.connect(path_to_database) as database:
        logging.debug('connected to database')
        cursor = database.cursor()
        query = f""" SELECT fullness FROM {user.state}_data WHERE login = ? """
        cursor.execute(query, (user.login,))
        fullness = cursor.fetchone()
        if fullness == None:
            raise HTTPException(status_code=404, detail="Login not found")
        if fullness[0] == False:
            raise HTTPException(status_code=423, detail="Fullness is false")
        query = f""" SELECT name, surname, phone FROM {user.state}_data WHERE login = ? """
        cursor.execute(query, (user.login,))
        user_info = cursor.fetchone()
        result = '~'.join(user_info)
    return result


@server.get('/get_user_{data}') #getting orders or templates
def get_user_data(data, user: User) -> str:
    logging.info(f"get user's {data}")
    result = 'done '
    with sqlite3.connect(path_to_database) as database:
        logging.debug('connected to database')
        cursor = database.cursor()
        query = """ SELECT login FROM client_data WHERE login = ? """
        cursor.execute(query, (user.login,))
        if cursor.fetchone() == None:
            raise HTTPException(status_code=404, detail="Login not found")
        query = f""" SELECT * FROM {data}_list WHERE login = ? """
        cursor.execute(query, (user.login,))
        data = cursor.fetchall()
        if data == None:
            return 'done not_found'
        for item in data:
            result += '~ '
            for elem in item:
                result += str(elem) + ' '
    return result


@server.post('/upload_user_info')
def upload_user_info(user: User, files: list[UploadFile]) -> str:
    result = 'done '
    profile_picture = files[0]
    passport = files[1]
    if user.name == None or user.surname == None or user.phone == None:
        raise HTTPException(status_code=422, detail="Need more information!")
    with sqlite3.connect(path_to_database) as database:
        cursor = database.cursor()
        query = f""" SELECT login from {user.state}_data WHERE login = ? """
        cursor.execute(query, (user.login,))
        if cursor.fetchone() == None:
            raise HTTPException(status_code=404, detail="Login not found")
    path_to_profile_picture = os.path.join(
        os.getcwd(), 'images', f'{user.state}_{user.login}_profile_picture.jpg')
    with open(path_to_profile_picture, mode='wb') as file:
        file.write(profile_picture.file)
    logging.debug('Done with profile picture')
    path_to_passport = os.path.join(
        os.getcwd(), 'images', f'{user.state}_{user.login}_passport.jpg')
    logging.debug('Try to get size of passport image')
    with open(path_to_passport, mode='wb') as file:
        file.write(passport.file)
    logging.debug('Done with passport picture')
    with sqlite3.connect(path_to_database) as database:
        logging.debug('connected to database')
        cursor = database.cursor()
        query = f""" UPDATE {user.state}_data SET name = ?, surname = ?, phone = ?, fullness = ? WHERE login = ?"""
        cursor.execute(query, (user.name, user.surname, user.phone, 1, user.login))
        database.commit()
    return result


@server.get('/get_user_picture/{picture}')
def get_user_file(picture, user: User) -> bytes: #getting user's passport or picture
    logging.info(f'Get profile picture of {user.state} {user.login}')
    with sqlite3.connect(path_to_database) as database:
        logging.debug('connected to database')
        cursor = database.cursor()
        query = f""" SELECT fullness FROM {user.state}_data WHERE login = ? """
        cursor.execute(query, (user.login,))
        fulness = cursor.fetchone()
        if fulness == None or fulness[0] == 0:
            raise HTTPException(status_code=404, detail="Item not found")
    path_to_picture = os.path.join(
        os.getcwd(), 'images', f'{user.state}_{user.login}_{picture}.jpg')
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

uvicorn.run(server, host = constants.IP, port = constants.PORT)
