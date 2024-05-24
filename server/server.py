from fastapi import FastAPI, HTTPException, UploadFile, Form, File
from fastapi.responses import FileResponse
from fastapi.logger import logger
from typing import Annotated
from AdditionalClasses import Order, User 
from rsa import decrypt
import uvicorn
import os
import sqlite3
import constants


path_to_database = os.path.join(
    os.getcwd(), 'database', 'database.db')
server = FastAPI()


def get_orders_json(elem: list):
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
def try_to_register(
        state: Annotated[str, Form()],
        login: Annotated[str, Form()],
        password: Annotated[UploadFile, File()]
    ) -> bool:
    with sqlite3.connect(path_to_database) as database:
        cursor = database.cursor()
        query = f""" SELECT login FROM {state}_data WHERE login = ? """
        cursor.execute(query, (login,))
        if cursor.fetchone() == None:
            query = f""" INSERT INTO {state}_data (login, password, fullness) VALUES (?, ?, ?) """
            cursor.execute(query, (login, password.file.read(), 0))
            database.commit()
            return True
        else:
            raise HTTPException(status_code=423, detail='Login already in use')


@server.get('/login')
def try_to_login(
    state: Annotated[str, Form()],
    login: Annotated[str, Form()],
    password: Annotated[UploadFile, File()]
) -> bool:
    with sqlite3.connect(path_to_database) as database:
        cursor = database.cursor()
        query = f""" SELECT password FROM {state}_data WHERE login = ? """
        cursor.execute(query, (login,))
        data = cursor.fetchone()
        if data == None:
            raise HTTPException(status_code=404, detail="Login not found")
        else:
            password = decrypt(password.file.read(), constants.privkey)
            correct_password = decrypt(data[0], constants.privkey)
            if password == correct_password:
                return True
            else:
                return False


@server.post('/new_order')
def make_new_order(order: Order) -> int:
    cur_id = -1
    with sqlite3.connect(path_to_database) as database:
        cursor = database.cursor()
        query = """ SELECT fullness FROM client_data WHERE login = ? """
        cursor.execute(query, (order.owner,))
        fullness = cursor.fetchone()
        if fullness == None:
            raise HTTPException(status_code=404, detail="Login not found")
        if fullness == 0:
            raise HTTPException(status_code=423, detail="Fullness is false")
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
        order.id = cur_id
        query = """ INSERT INTO orders_list (id, owner, name, cost, description, start, finish, supplier) VALUES (?, ?, ?, ?, ?, ?, ?, ?) """
        cursor.execute(query, order.get_tuple())
        database.commit()
    return cur_id


@server.post('/new_template')
def make_new_template(order: Order) -> bool:
    with sqlite3.connect(path_to_database) as database:
        cursor = database.cursor()
        query = """ SELECT fullness FROM client_data WHERE login = ? """
        cursor.execute(query, (order.owner,))
        fullness = cursor.fetchone()
        if fullness == None:
            raise HTTPException(status_code=404, detail="Login not found")
        if fullness == 0:
            raise HTTPException(status_code=423, detail="Fullness is false")
        query = """ INSERT INTO templates_list (id, owner, name, cost, description, start, finish, supplier) VALUES (?, ?, ?, ?, ?, ?, ?, ?) """
        cursor.execute(query, order.get_tuple())
        database.commit()
    return True


@server.put('/take_order/{order_id}')
def take_order(order_id: int, user: User) -> bool:
    with sqlite3.connect(path_to_database) as database:
        cursor = database.cursor()
        query = """ SELECT fullness FROM delivery_data WHERE login = ? """
        cursor.execute(query, (user.login,))
        fullness = cursor.fetchone()
        if fullness == None:
            raise HTTPException(status_code=404, detail="Login not found")
        if fullness == 0:
            raise HTTPException(status_code=423, detail="Fullness is false")
        query = """ SELECT id FROM orders_list WHERE id = ? """
        cursor.execute(query, (order_id,))
        if cursor.fetchone() == None:
            raise HTTPException(status_code=404, detail="Order not found")
        query = """ UPDATE orders_list SET supplier = ? WHERE id = ? """
        cursor.execute(query, (user.login, order_id))
        database.commit()
    return True


@server.put('/complete_order/{order_id}')
def complete_order(order_id: int) -> int:
    with sqlite3.connect(path_to_database) as database:
        cursor = database.cursor()
        query = """ SELECT * FROM orders_list WHERE id = ? """
        cursor.execute(query, (order_id,))
        order_info = cursor.fetchone()
        if order_info == None:
            raise HTTPException(status_code=404, detail="Order not found")
        query = """ DELETE FROM orders_list WHERE id = ? """
        cursor.execute(query, (order_id,))
        query = """ SELECT COUNT(*) FROM archive """
        cursor.execute(query)
        cur_id = cursor.fetchone()[0]
        query = """ INSERT INTO archive (id, owner, name, cost, description, start, finish, supplier) VALUES (?, ?, ?, ?, ?, ?, ?, ?) """
        cursor.execute(query, (cur_id,) + order_info[1:])
        database.commit()
    return cur_id


@server.delete('/delete_order/{order_id}')
def delete_order(order_id: int) -> bool:
    with sqlite3.connect(path_to_database) as database:
        cursor = database.cursor()
        query = """ SELECT * FROM orders_list WHERE id = ? """
        cursor.execute(query, (order_id,))
        order_info = cursor.fetchone()
        if order_info == None:
            raise HTTPException(status_code=404, detail="Order not found")
        query = """ DELETE FROM orders_list WHERE id = ? """
        cursor.execute(query, (order_id,))
        database.commit()
    return True


@server.get('/get_profile_fullness')
def get_profile_fullness(user: User) -> bool:
    result = True
    with sqlite3.connect(path_to_database) as database:
        cursor = database.cursor()
        query = f""" SELECT fullness FROM {user.state}_data WHERE login = ? """
        cursor.execute(query, (user.login,))
        data = cursor.fetchone()
        if data == None:
            raise HTTPException(status_code=404, detail="Login not found")
        result = data[0]
    return result


@server.get('/get_user_info')
def get_user_info(user: User) -> dict:
    with sqlite3.connect(path_to_database) as database:
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
    result = {
        'name': user_info[0],
        'surname': user_info[1],
        'phone': user_info[2]
    }
    return result


@server.get('/get_user_picture/{picture}')
def get_user_file(picture, user: User) -> bytes: #getting user's passport or picture
    with sqlite3.connect(path_to_database) as database:
        cursor = database.cursor()
        query = f""" SELECT fullness FROM {user.state}_data WHERE login = ? """
        cursor.execute(query, (user.login,))
        fullness = cursor.fetchone()
        if fullness == None:
            raise HTTPException(status_code=404, detail="Login not found")
        if fullness[0] == 0:
            raise HTTPException(status_code=423, detail="Fullness is false")
    path_to_picture = os.path.join(
        os.getcwd(), 'images', f'{user.state}_{user.login}_{picture}.jpg')
    return FileResponse(path=path_to_picture)


@server.get('/get_active_orders')
def get_active_orders(user: User) -> list:
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


@server.get('/get_archive_orders')
def get_archive_orders(user: User) -> list:
    result = []
    with sqlite3.connect(path_to_database) as database:
        cursor = database.cursor()
        relation = 'owner' #if it is a client we get orders by owner
        if user.state == 'delivery':
            relation = 'supplier'
        query = f""" SELECT fullness FROM {user.state}_data WHERE login = ? """
        cursor.execute(query, (user.login,))
        fullness = cursor.fetchone()
        if fullness == None:
            raise HTTPException(status_code=404, detail="Login not found")
        if fullness[0] == 0:
            raise HTTPException(status_code=423, detail="Fullness is false")
        query = f""" SELECT * FROM archive WHERE {relation} = ? """
        cursor.execute(query, (user.login,))
        for elem in cursor.fetchall():
            order = get_orders_json(elem)
            result.append(order)
    return result


@server.get('/get_free_orders')
def get_free_orders(user: User) -> list:
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
        query = """ SELECT * FROM orders_list WHERE supplier IS NULL """
        cursor.execute(query)
        for elem in cursor.fetchall():
            order = get_orders_json(elem)
            result.append(order)
    return result


@server.get('/get_user_orders') 
def get_user_orders(user: User) -> list:
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
def get_user_templates(user: User) -> list:
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
)-> bool:
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
    return True


with sqlite3.connect(path_to_database) as database:
    cursor = database.cursor()
    query = """ CREATE TABLE IF NOT EXISTS client_data ( login TEXT, password BLOB, name TEXT, surname TEXT, phone TEXT, fullness INTEGER ) """
    cursor.execute(query)
    query = """ CREATE TABLE IF NOT EXISTS delivery_data ( login TEXT, password BLOB, name TEXT, surname TEXT, phone TEXT, fullness INTEGER ) """
    cursor.execute(query)
    query = """ CREATE TABLE IF NOT EXISTS orders_list ( id INTEGER, owner TEXT, name TEXT, cost INTEGER, description TEXT, start TEXT, finish TEXT, supplier TEXT ) """
    cursor.execute(query)
    query = """ CREATE TABLE IF NOT EXISTS templates_list ( id INTEGER, owner TEXT, name TEXT, cost INTEGER, description TEXT, start TEXT, finish TEXT, supplier TEXT ) """
    cursor.execute(query)
    query = """ CREATE TABLE IF NOT EXISTS archive ( id INTEGER, owner TEXT, name TEXT, cost INTEGER, description TEXT, start TEXT, finish TEXT, supplier TEXT ) """
    cursor.execute(query)
    database.commit()

uvicorn.run(server, host = constants.IP, port = constants.PORT)
