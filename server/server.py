from fastapi import FastAPI, HTTPException, UploadFile, Form, File
from fastapi.responses import FileResponse
from fastapi.logger import logger
from pydantic import BaseModel
from typing import List, Annotated
from AdditionalClasses import Order, User 
import uvicorn
import os
import logging
import sqlite3
import constants


path_to_database = os.path.join(
    os.getcwd(), 'database', 'database.db')
server = FastAPI()


def get_orders_json(elem: List):
    order = {
        'id': elem[0],
        'owner': elem[1],
        'name': elem[2],
        'cost': elem[3],
        'description': elem[4],
        'start': elem[5],
        'finish': elem[6],
        'supplier': elem[7],
    }
    return order


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
        query = """ INSERT INTO orders_list (id, owner, name, cost, description, start, finish, supplier) VALUES (?, ?, ?, ?, ?, ?, ?, ?) """
        cursor.execute(query, (cur_id,) + order.get_tuple())
        database.commit()
    return f"done {cur_id}"


@server.post('/new_template')
def make_new_template(order: Order) -> str:
    with sqlite3.connect(path_to_database) as database:
        cursor = database.cursor()
        query = """ SELECT login FROM client_data WHERE login = ? """
        cursor.execute(query, (order.owner,))
        if cursor.fetchone() == None:
            raise HTTPException(status_code=404, detail="Item not found")
        query = """ INSERT INTO templates_list (id, owner, name, cost, description, start, finish, supplier) VALUES (?, ?, ?, ?, ?, ?, ?) """
        cursor.execute(query, (-1,) + order.get_tuple())
        database.commit()
    return 'done'


@server.get('/get_profile_fullness')
def get_profile_fullness(user: User) -> bool:
    result = True
    with sqlite3.connect(path_to_database) as database:
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


@server.get('/get_user_picture/{picture}')
def get_user_file(picture, user: User) -> bytes: #getting user's passport or picture
    with sqlite3.connect(path_to_database) as database:
        logging.debug('connected to database')
        cursor = database.cursor()
        query = f""" SELECT fullness FROM {user.state}_data WHERE login = ? """
        cursor.execute(query, (user.login,))
        fullness = cursor.fetchone()
        if fullness == None:
            raise HTTPException(status_code=404, detail="Item not found")
        if fullness[0] == 0:
            raise HTTPException(status_code=423, detail="Fullness is false")
    path_to_picture = os.path.join(
        os.getcwd(), 'images', f'{user.state}_{user.login}_{picture}.jpg')
    return FileResponse(path=path_to_picture)


@server.get('/get_active_orders')
def get_active_orders(user: User) -> List:
    result = []
    with sqlite3.connect(path_to_database) as database:
        cursor = database.cursor()
        query = """ SELECT fullness FROM delivery_data WHERE login = ? """
        cursor.execute(query, (user.login,))
        fullness = cursor.fetchone()
        if fullness == None:
            raise HTTPException(status_code=404, detail="Login not found")
        if fullness[0] == 0:
            raise HTTPException(status_code=423, detail="Fullness is false")
        query = """ SELECT * FROM orders_list WHERE supplier = ? """
        cursor.execute(query, (user.login,))
        for elem in cursor.fetchall():
            order = get_orders_json(elem)
            result.append(order)
    return result


@server.get('/get_user_orders') 
def get_user_orders(user: User) -> List:
    result = []
    with sqlite3.connect(path_to_database) as database:
        cursor = database.cursor()
        query = """ SELECT login FROM client_data WHERE login = ? """
        cursor.execute(query, (user.login,))
        if cursor.fetchone() == None:
            raise HTTPException(status_code=404, detail="Login not found")
        query = f""" SELECT * FROM orders_list WHERE owner = ? """
        cursor.execute(query, (user.login,))
        for elem in cursor.fetchall():
            order = get_orders_json(elem)
            result.append(order)
    return result


@server.get('/get_user_templates') 
def get_user_templates(user: User) -> List:
    result = []
    with sqlite3.connect(path_to_database) as database:
        cursor = database.cursor()
        query = """ SELECT login FROM client_data WHERE login = ? """
        cursor.execute(query, (user.login,))
        if cursor.fetchone() == None:
            raise HTTPException(status_code=404, detail="Login not found")
        query = f""" SELECT * FROM templates_list WHERE owner = ? """
        cursor.execute(query, (user.login,))
        for elem in cursor.fetchall():
            order = get_orders_json(elem)
            result.append(order)
    return result


@server.post('/upload_user_info')
def upload_user_info(
    state: Annotated[str, Form()],
    login: Annotated[str, Form()],
    name: Annotated[str, Form()],
    surname: Annotated[str, Form()],
    phone: Annotated[str, Form()],
    profile_picture: Annotated[UploadFile, File()],
    passport: Annotated[UploadFile, File()]
)-> str:
    if name == None or surname == None or phone == None:
        raise HTTPException(status_code=422, detail="Need more information!")
    with sqlite3.connect(path_to_database) as database:
        cursor = database.cursor()
        query = f""" SELECT login from {state}_data WHERE login = ? """
        cursor.execute(query, (login,))
        if cursor.fetchone() == None:
            raise HTTPException(status_code=404, detail="Login not found")
    path_to_profile_picture = os.path.join(
        os.getcwd(), 'images', f'{state}_{login}_profile_picture.jpg')
    with open(path_to_profile_picture, mode='wb') as File:
        File.write(profile_picture.file.read())
    path_to_passport = os.path.join(
        os.getcwd(), 'images', f'{state}_{login}_passport.jpg')
    with open(path_to_passport, mode='wb') as File:
        File.write(passport.file.read())
    with sqlite3.connect(path_to_database) as database:
        cursor = database.cursor()
        query = f""" UPDATE {state}_data SET name = ?, surname = ?, phone = ?, fullness = ? WHERE login = ?"""
        cursor.execute(query, (name, surname, phone, 1, login)) 
        database.commit()
    return 'done'


logging.basicConfig(level=logging.INFO, filename="loggings.log",
                    filemode="w", format="%(asctime)s %(levelname)s %(message)s")
with sqlite3.connect(path_to_database) as database:
    cursor = database.cursor()
    query = """ CREATE TABLE IF NOT EXISTS client_data ( login TEXT, password TEXT, name TEXT, surname TEXT, phone TEXT, fullness INTEGER ) """
    cursor.execute(query)
    query = """ CREATE TABLE IF NOT EXISTS delivery_data ( login TEXT, password TEXT, name TEXT, surname TEXT, phone TEXT, fullness INTEGER ) """
    cursor.execute(query)
    query = """ CREATE TABLE IF NOT EXISTS orders_list ( id INTEGER, owner TEXT, name TEXT, cost INTEGER, description TEXT, start TEXT, finish TEXT, supplier TEXT ) """
    cursor.execute(query)
    query = """ CREATE TABLE IF NOT EXISTS templates_list ( id INTEGER, owner TEXT, name TEXT, cost INTEGER, description TEXT, start TEXT, finish TEXT, supplier TEXT ) """
    cursor.execute(query)
    database.commit()

uvicorn.run(server, host = constants.IP, port = constants.PORT)
