from fastapi import FastAPI, HTTPException, UploadFile, Form, File
from fastapi.responses import FileResponse
from fastapi.logger import logger
from typing import Annotated
from AdditionalClasses import Order, User 
from rsa import decrypt
from datetime import datetime
from random import randint
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
        'time': datetime.strptime(elem[8], "%Y/%m/%d %H:%M"),
        'fee': elem[9]
    }
    if len(elem) == 11:
        order['last_cost'] = elem[10]
    return order


def get_order_id(table: str) -> int:
    with sqlite3.connect(path_to_database) as database:
        cursor = database.cursor()
        query = f""" SELECT id FROM {table} ORDER BY id """
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
    return cur_id


def time_to_str(time: datetime) -> str:
    year = time.year 
    month = f'0{time.month}'
    if time.month >= 10:
        month = f'{time.month}'
    day = f'0{time.day}'
    if time.day >= 10:
        day = f'{time.day}'
    hour = f'0{time.hour}'
    if time.hour >= 10:
        hour = f'{time.hour}'
    minute = f'0{time.minute}'
    if time.minute >= 10:
        minute = f'{time.minute}'
    return f"{year}/{month}/{day} {hour}:{minute}"


def update_auction_orders() -> None:
    with sqlite3.connect(path_to_database) as database:
        cursor = database.cursor()
        time = datetime.now() + constants.delta['UTC'] + constants.delta['DAY']
        time = time_to_str(time)
        query = """ SELECT * FROM auction_orders WHERE time < ? """
        cursor.execute(query, (time,))
        orders_info = cursor.fetchall()
        query = """ DELETE FROM auction_orders WHERE time < ? """
        cursor.execute(query, (time,))
        for elem in orders_info:
            table = 'active_orders'
            cost = elem[-1]
            if elem[-4] == None:
                table = 'free_orders'
                cost = elem[3]
            cur_id = get_order_id(table)
            query = f""" INSERT INTO {table} (id, owner, name, cost, description, start, finish, supplier, time, fee) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?) """
            cursor.execute(query, (cur_id,) + elem[1:3] + (cost,) + elem[4:-1])
        database.commit()
    return None
        

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


@server.post('/new_order/{type_of_order}')
def make_new_order(type_of_order: str, order: Order) -> int:
    update_auction_orders()
    order.id = get_order_id(f'{type_of_order}_orders')
    with sqlite3.connect(path_to_database) as database:
        cursor = database.cursor()
        query = """ SELECT fullness FROM client_data WHERE login = ? """
        cursor.execute(query, (order.owner,))
        fullness = cursor.fetchone()
        if fullness == None:
            raise HTTPException(status_code=404, detail="Login not found")
        if fullness == 0:
            raise HTTPException(status_code=403, detail="Fullness is false")
        query = f""" INSERT INTO {type_of_order}_orders (id, owner, name, cost, description, start, finish, supplier, time, fee) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?) """
        cursor.execute(query, order.get_tuple())
        database.commit()
    return order.id


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
            raise HTTPException(status_code=403, detail="Fullness is false")
        query = """ INSERT INTO templates_list (id, owner, name, cost, description, start, finish, supplier, time, fee) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?) """
        cursor.execute(query, order.get_tuple())
        database.commit()
    return True


@server.post('/new_chat') 
def make_new_chat(
    delivery: Annotated[str, Form()],
    client: Annotated[str, Form()],
    order: Annotated[str, Form()]
) -> int:
    with sqlite3.connect(path_to_database) as database:
        cursor = database.cursor()
        query = """ SELECT MAX(id) FROM chats """
        cursor.execute(query)
        max_id = cursor.fetchone()
        cur_id = 0
        if max_id != None:
            cur_id = max_id[0] + 1
        time = datetime.now() + constants.delta['UTC']
        time = time_to_str(time)
        query = """ INSERT INTO chats ( id, delivery, client, name, message, owner, time ) VALUES (?, ?, ?, ?, ?, ?, ?) """
        cursor.execute(query, (cur_id, delivery, client, order, 'Initial message', 'Server', time))
        database.commit()
    return cur_id


@server.post('/send_message/{chat_id}')
def send_message(
    chat_id: int,
    user: Annotated[User, Form()],
    message: Annotated[str, Form()]
) -> bool:
    with sqlite3.connect(path_to_database) as database:
        cursor = database.cursor()
        query = f""" SELECT {user.state} FROM chats WHERE id = ? """
        cursor.execute(query, (chat_id,))
        member = cursor.fetchone()
        if member == None:
            raise HTTPException(status_code=404, detail='Chat not found')
        if member[0] != user.login:
            raise HTTPException(states_code=403, detail='User is not a chat member')
        query = """ SELECT delivery, client, name FROM chats WHERE id = ? """
        cursor.execute(query, (chat_id,))
        chat_info = cursor.fetchone()
        time = datetime.now() + constants.delta['UTC']
        time = time_to_str(time)
        query = """ INSERT INTO chats ( id, delivery, client, name, message, owner, time ) VALUES (?, ?, ?, ?, ?, ?, ?) """
        cursor.execute(query, (chat_id,) + chat_info + (message, user.login, time))
        database.commit()
    return True


@server.put('/take_order/{type_of_order}/{order_id}')
def take_order(type_of_order: str, order_id: int, user: User) -> int:
    update_auction_orders()
    if get_user_rating(user) < 3.5:
        raise HTTPException(status_code=403, detail="Rating is too low")
    if user.state == 'client':
        raise HTTPException(status_code=423, detail="It is not a client case")
    with sqlite3.connect(path_to_database) as database:
        cursor = database.cursor()
        query = """ SELECT fullness FROM delivery_data WHERE login = ? """
        cursor.execute(query, (user.login,))
        fullness = cursor.fetchone()
        if fullness == None:
            raise HTTPException(status_code=404, detail="Login not found")
        if fullness == 0:
            raise HTTPException(status_code=403, detail="Fullness is false")
        query = f""" SELECT * FROM {type_of_order}_orders WHERE id = ? """
        cursor.execute(query, (order_id,))
        order_info = cursor.fetchone()
        if order_info == None:
            raise HTTPException(status_code=404, detail="Order not found")
        query = f""" DELETE FROM {type_of_order}_orders WHERE id = ? """
        cursor.execute(query, (order_id,))
        if type_of_order == 'free':
            type_of_order = 'active'
        cost = order_info[3]
        last_cost = int(cost)
        if type_of_order == 'auction':
            cost = int(cost*(0.95))
        cur_id = get_order_id(f'{type_of_order}_orders')
        supplier = user.login
        query = f""" INSERT INTO {type_of_order}_orders (id, owner, name, cost, description, start, finish, supplier, time, fee) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?) """
        cursor.execute(query, (cur_id,) + order_info[1:3] + (cost,) + order_info[4:7] + (supplier,) + order_info[8:10])
        if type_of_order == 'auction':
            query = f""" UPDATE {type_of_order}_orders SET last_cost = ? WHERE id = ? """
            cursor.execute(query, (last_cost, cur_id))
        database.commit()
    return cur_id


@server.put('/edit_order/{type_of_order}/{order_id}')
def edit_order(type_of_order: str, order_id: int, order: Order) -> int:
    update_auction_orders()
    with sqlite3.connect(path_to_database) as database:
        cursor = database.cursor()
        query = """ SELECT fullness FROM client_data WHERE login = ? """
        cursor.execute(query, (order.owner,))
        fullness = cursor.fetchone()
        if fullness == None:
            raise HTTPException(status_code=404, detail="Login not found")
        if fullness == 0:
            raise HTTPException(status_code=403, detail="Fullness is false")
        query = f""" UPDATE {type_of_order}_orders
                SET (owner, name, cost, description, start, finish, supplier, time) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                WHERE id = ? """
        cursor.execute(query, order.get_tuple()[1:-1] + (order_id,))
        database.commit()
    return order.id


@server.put('/start_order/{order_id}')
def start_order(order_id: int) -> int:
    with sqlite3.connect(path_to_database) as database:
        cursor = database.cursor()
        query = """ SELECT * FROM active_orders WHERE id = ? """
        cursor.execute(query, (order_id,))
        order_info = cursor.fetchone()
        if order_info == None:
            raise HTTPException(status_code=404, detail="Order not found")
        query = """ DELETE FROM active_orders WHERE id = ? """
        cursor.execute(query, (order_id,))
        cur_id = get_order_id('in_process_orders')
        time = datetime.now() + constants.delta['UTC']
        time = time_to_str(time)
        fee = order_info[-1]
        code = randint(1000, 9999)
        query = """ INSERT INTO in_process_orders (id, owner, name, cost, description, start, finish, supplier, time, fee, code) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?) """
        cursor.execute(query, (cur_id,) + order_info[1:-2] + (time, fee, code))
        database.commit()
    return cur_id


@server.put('/complete_order/{order_id}')
def complete_order(
    order_id: int,
    code: Annotated[int, Form()]
    ) -> int:
    with sqlite3.connect(path_to_database) as database:
        cursor = database.cursor()
        query = """ SELECT * FROM in_process_orders WHERE id = ? """
        cursor.execute(query, (order_id,))
        order_info = cursor.fetchone()
        if order_info == None:
            raise HTTPException(status_code=404, detail="Order not found")
        if order_info[10] != code:
            raise HTTPException(status_code=403, detail="Incorrect code")
        query = """ DELETE FROM in_process_orders WHERE id = ? """
        cursor.execute(query, (order_id,))
        cur_id = get_order_id('archive')
        time = datetime.now() + constants.delta['UTC']
        time = time_to_str(time)
        fee = order_info[-2]
        query = """ INSERT INTO archive (id, owner, name, cost, description, start, finish, supplier, time, fee) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?) """
        cursor.execute(query, (cur_id,) + order_info[1:8] + (time, fee))
        database.commit()
    return cur_id


@server.put('/rate_order/{order_id}')
def rate_order(
    order_id: int,
    rating: Annotated[float, Form()]
    ) -> bool:
    with sqlite3.connect(path_to_database) as database:
        cursor = database.cursor()
        query = """ SELECT rating FROM archive WHERE id = ? """
        cursor.execute(query, (order_id,))
        order_rating = cursor.fetchone()
        if order_rating == None:
            raise HTTPException(status_code=404, detail="Order not found")
        if order_rating[0] != None:
            raise HTTPException(status_code=423, detail="Order is already rated")
        query = """ UPDATE archive SET rating = ? WHERE id = ? """
        cursor.execute(query, (rating, order_id))
        database.commit()
    return True


@server.delete('/delete_order/{type_of_order}/{order_id}')
def delete_order(type_of_order: str, order_id: int) -> bool:
    with sqlite3.connect(path_to_database) as database:
        cursor = database.cursor()
        query = f""" SELECT * FROM {type_of_order}_orders WHERE id = ? """
        cursor.execute(query, (order_id,))
        order_info = cursor.fetchone()
        if order_info == None:
            raise HTTPException(status_code=404, detail="Order not found")
        query = f""" DELETE FROM {type_of_order}_orders WHERE id = ? """
        cursor.execute(query, (order_id,))
        database.commit()
    return True


@server.get('/get_user_chats')
def get_user_chats(user: User) -> list:
    result = []
    with sqlite3.connect(path_to_database) as database:
        cursor = database.cursor()
        query = f""" SELECT DISTINCT id, name FROM chats WHERE {user.state} = ? """
        cursor.execute(query, (user.login,))
        for chat_info in cursor.fetchall():
            result.append({
                'id': chat_info[0],
                'name': chat_info[1]
            })
    return result


@server.get('/get_chat_content')
def get_chat_content(
    chat_id = Annotated[int, Form()]
) -> dict:
    result: dict
    with sqlite3.connect(path_to_database) as database:
        cursor = database.cursor()
        query = """ SELECT name, client, delivery FROM chats WHERE id = ? """
        cursor.execute(query, (chat_id,))
        chat_info = cursor.fetchone()
        result['info'] = {
            'name': chat_info[0],
            'client': chat_info[1],
            'delivery': chat_info[2]
        }
        query = """ SELECT message, owner, time FROM chats WHERE id = ?, owner NOT IN (Server,) ORDER BY time """
        cursor.execute(query, (chat_id,))
        chat_content: list
        for content in cursor.fetchall():
            chat_content.append({
                'message': content[0],
                'owner': content[1],
                'time': content[2]
            })
        result['content'] = chat_content 
    return result


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
            raise HTTPException(status_code=403, detail="Fullness is false")
        query = f""" SELECT name, surname, phone FROM {user.state}_data WHERE login = ? """
        cursor.execute(query, (user.login,))
        user_info = cursor.fetchone()
    result = {
        'name': user_info[0],
        'surname': user_info[1],
        'phone': user_info[2]
    }
    return result


@server.get('/get_user_rating')
def get_user_rating(user: User) -> float:
    result = 6.0
    with sqlite3.connect(path_to_database) as database:
        cursor = database.cursor()
        query = f""" SELECT fullness FROM {user.state}_data WHERE login = ? """
        cursor.execute(query, (user.login,))
        fullness = cursor.fetchone()
        if fullness == None:
            raise HTTPException(status_code=404, detail="Login not found")
        if fullness[0] == False:
            raise HTTPException(status_code=403, detail="Fullness is false")
        time = datetime.now() + constants.delta['UTC'] - constants.delta['MONTH']
        time = time_to_str(time)
        query = """ SELECT COUNT(rating) FROM archive WHERE supplier = ? AND time > ? """
        cursor.execute(query, (user.login, time))
        cnt_of_marks = cursor.fetchone()[0]
        if cnt_of_marks >= 5:
            query = """ SELECT AVG(rating) FROM archive WHERE supplier = ? AND time > ? """
            cursor.execute(query, (user.login, time))
            result = cursor.fetchone()[0]
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
            raise HTTPException(status_code=403, detail="Fullness is false")
    path_to_picture = os.path.join(
        os.getcwd(), 'images', f'{user.state}_{user.login}_{picture}.jpg')
    return FileResponse(path=path_to_picture)


@server.get('/get_active_orders')
def get_active_orders(user: User) -> list:
    update_auction_orders()
    result = []
    with sqlite3.connect(path_to_database) as database:
        cursor = database.cursor()
        query = """ SELECT fullness FROM delivery_data WHERE login = ? """
        cursor.execute(query, (user.login,))
        fullness = cursor.fetchone()
        if fullness == None:
            raise HTTPException(status_code=404, detail="Login not found")
        if fullness[0] == 0:
            raise HTTPException(status_code=403, detail="Fullness is false")
        query = """ SELECT * FROM active_orders WHERE supplier = ? """
        cursor.execute(query, (user.login,))
        for elem in cursor.fetchall():
            order = get_orders_json(elem)
            result.append(order)
    return result


@server.get('/get_auction_orders')
def get_auction_orders(user: User) -> list:
    update_auction_orders()
    result = []
    with sqlite3.connect(path_to_database) as database:
        cursor = database.cursor()
        query = """ SELECT fullness FROM delivery_data WHERE login = ? """
        cursor.execute(query, (user.login,))
        fullness = cursor.fetchone()
        if fullness == None:
            raise HTTPException(status_code=404, detail="Login not found")
        if fullness[0] == 0:
            raise HTTPException(status_code=403, detail="Fullness is false")
        query = """ SELECT * FROM auction_orders """
        cursor.execute(query)
        for elem in cursor.fetchall():
            order = get_orders_json(elem)
            result.append(order)
    return result


@server.get('/get_in_process_orders')
def get_in_process_orders(user: User) -> list:
    result = []
    with sqlite3.connect(path_to_database) as database:
        cursor = database.cursor()
        query = """ SELECT fullness FROM delivery_data WHERE login = ? """
        cursor.execute(query, (user.login,))
        fullness = cursor.fetchone()
        if fullness == None:
            raise HTTPException(status_code=404, detail="Login not found")
        if fullness[0] == 0:
            raise HTTPException(status_code=403, detail="Fullness is false")
        query = """ SELECT * FROM in_process_orders WHERE supplier = ? """
        cursor.execute(query, (user.login,))
        for elem in cursor.fetchall():
            order = get_orders_json(elem)
            if user.state == 'client':
                order['code'] = elem[9]
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
            raise HTTPException(status_code=403, detail="Fullness is false")
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
            raise HTTPException(status_code=403, detail="Fullness is false")
        query = """ SELECT * FROM free_orders """
        cursor.execute(query)
        for elem in cursor.fetchall():
            order = get_orders_json(elem)
            result.append(order)
    return result


@server.get('/get_user_orders')
def get_user_orders(user: User) -> dict:
    result = {}
    with sqlite3.connect(path_to_database) as database:
        cursor = database.cursor()
        query = """ SELECT fullness FROM client_data WHERE login = ? """
        cursor.execute(query, (user.login,))
        fullness = cursor.fetchone()
        if fullness == None:
            raise HTTPException(status_code=404, detail="Login not found")
        if fullness[0] == 0:
            raise HTTPException(status_code=403, detail="Fullness is false")
        query = """ SELECT * FROM free_orders WHERE owner = ? """
        free_orders = []
        cursor.execute(query, (user.login,))
        for elem in cursor.fetchall():
            order = get_orders_json(elem)
            free_orders.append(order)
        result['free_orders'] = free_orders
        query = """ SELECT * FROM active_orders WHERE owner = ? """
        active_orders = []
        cursor.execute(query, (user.login,))
        for elem in cursor.fetchall():
            order = get_orders_json(elem)
            active_orders.append(order)
        result['active_orders'] = active_orders
        query = """ SELECT * FROM auction_orders WHERE owner = ? """
        auction_orders = []
        cursor.execute(query, (user.login,))
        for elem in cursor.fetchall():
            order = get_orders_json(elem)
            auction_orders.append(order)
        result['auction_orders'] = auction_orders
        query = """ SELECT * FROM in_process_orders WHERE owner = ? """
        in_process_orders = []
        cursor.execute(query, (user.login,))
        for elem in cursor.fetchall():
            order = get_orders_json(elem)
            in_process_orders.append(order)
        result['in_process_orders'] = in_process_orders
    return result


@server.get('/get_user_orders/{type_of_order}')
def get_user_orders_by_type(type_of_order: str, user: User) -> list:
    result = []
    with sqlite3.connect(path_to_database) as database:
        cursor = database.cursor()
        query = """ SELECT fullness FROM client_data WHERE login = ? """
        cursor.execute(query, (user.login,))
        fullness = cursor.fetchone()
        if fullness == None:
            raise HTTPException(status_code=404, detail="Login not found")
        if fullness[0] == 0:
            raise HTTPException(status_code=403, detail="Fullness is false")
        query = f""" SELECT * FROM {type_of_order}_orders WHERE owner = ? """
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
        query = f""" SELECT login FROM {state}_data WHERE login = ? """
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
    query = """ CREATE TABLE IF NOT EXISTS client_data ( login TEXT PRIMARY KEY, password BLOB, name TEXT, surname TEXT, phone TEXT, fullness INTEGER ) """
    cursor.execute(query)
    query = """ CREATE TABLE IF NOT EXISTS delivery_data ( login TEXT PRIMARY KEY, password BLOB, name TEXT, surname TEXT, phone TEXT, fullness INTEGER ) """
    cursor.execute(query)
    query = """ CREATE TABLE IF NOT EXISTS auction_orders ( id INTEGER PRIMARY KEY, owner TEXT, name TEXT, cost INTEGER, description TEXT, start TEXT, finish TEXT, supplier TEXT, time TEXT, fee INTEGER, last_cost INTEGER ) """
    cursor.execute(query)
    query = """ CREATE TABLE IF NOT EXISTS free_orders ( id INTEGER PRIMARY KEY, owner TEXT, name TEXT, cost INTEGER, description TEXT, start TEXT, finish TEXT, supplier TEXT, time TEXT, fee INTEGER ) """
    cursor.execute(query)
    query = """ CREATE TABLE IF NOT EXISTS active_orders ( id INTEGER PRIMARY KEY, owner TEXT, name TEXT, cost INTEGER, description TEXT, start TEXT, finish TEXT, supplier TEXT, time TEXT, fee INTEGER ) """
    cursor.execute(query)
    query = """ CREATE TABLE IF NOT EXISTS in_process_orders ( id INTEGER PRIMARY KEY, owner TEXT, name TEXT, cost INTEGER, description TEXT, start TEXT, finish TEXT, supplier TEXT, time TEXT, fee INTEGER, code INTEGER ) """
    cursor.execute(query)
    query = """ CREATE TABLE IF NOT EXISTS templates_list ( id INTEGER PRIMARY KEY, owner TEXT, name TEXT, cost INTEGER, description TEXT, start TEXT, finish TEXT, supplier TEXT, time TEXT, fee INTEGER ) """
    cursor.execute(query)
    query = """ CREATE TABLE IF NOT EXISTS archive ( id INTEGER PRIMARY KEY, owner TEXT, name TEXT, cost INTEGER, description TEXT, start TEXT, finish TEXT, supplier TEXT, time TEXT, fee INTEGER, rating INTEGER ) """
    cursor.execute(query)
    query = """ CREATE TABLE IF NOT EXISTS chats ( id INTEGER, delivery TEXT, client TEXT, name TEXT, message TEXT, owner TEXT, time TEXT ) """
    cursor.execute(query)
    database.commit()

uvicorn.run(server, host = constants.IP, port = constants.PORT)
