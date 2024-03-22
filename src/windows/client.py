import os

from kivy.uix.screenmanager import Screen
from kivy.uix.button import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup

from windows.baseclass import ColorAnimBase
from windows.server_logic.server_interaction import ServerLogic

class ClientOrderPreview(ButtonBehavior, BoxLayout):
    def __init__(self, order_id, description, name, price, start, finish, courier):
        super().__init__()
        self.order_id = order_id
        self.description = description
        self.order_name = name
        self.price = price
        self.start = start
        self.finish = finish
        self.courier = courier

class ClientTemplatePreview(ButtonBehavior, BoxLayout):
    def __init__(self, name, price, description, start, finish):
        super().__init__()
        self.template_name = name
        self.price = price
        self.description = description
        self.start = start
        self.finish = finish

class ClientSide(Screen, ColorAnimBase, ServerLogic):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.client_main_frame.current = 'client_orders'

    def quit(self):
        path_to_login = os.path.join(os.getcwd(), 'src', 'windows', 'server_logic', 'state_login')
        path_to_fullname = os.path.join(os.getcwd(), 'src', 'windows', 'profile', 'fullname')
        path_to_avatar = os.path.join(os.getcwd(), 'src', 'windows', 'profile', 'avatar.jpg')
        path_to_no_avatar = os.path.join(os.getcwd(), 'src', 'windows', 'profile', 'no_avatar.jpg')
        with open(path_to_login, 'wb'):
            pass
        with open(path_to_fullname, 'wb'):
            pass
        if os.path.isfile(path_to_avatar):
            os.remove(path_to_avatar)
        self.manager.transition.direction = 'down'
        self.manager.current = 'auth'
        self.client_orders_scrollview.clear_widgets()
        self.client_main_frame.current = 'client_orders'
        self.icon_chat.source, self.icon_list.source, self.icon_user.source = 'img/chat.png', 'img/bold_list.png', 'img/user.png'
        self.active_orders.animated_color , self.template_orders.animated_color = (217/255, 217/255, 217/255, 0), (217/255, 217/255, 217/255, 0)
        self.user_fullname.text = '[b]Неизвестно[/b]'
        self.user_avatar.path = path_to_no_avatar

    def switch_main_to(self, screen):
        if self.client_main_frame.current != screen:
            self.client_main_frame.current = screen
        if screen == 'client_chat':
            self.icon_chat.source, self.icon_list.source, self.icon_user.source = 'img/bold_chat.png', 'img/list.png', 'img/user.png'
        elif screen == 'client_orders':
            self.icon_chat.source, self.icon_list.source, self.icon_user.source = 'img/chat.png', 'img/bold_list.png', 'img/user.png'
        elif screen == 'client_profile':
            self.icon_chat.source, self.icon_list.source, self.icon_user.source = 'img/chat.png', 'img/list.png', 'img/bold_user.png'

    def show_client_data(self, info):
        if (info != 'orders' and info != 'templates'):
            Popup(title='Ошибка', content=Label(text='FATAL'), size_hint=(0.8, 0.2)).open()
        self.client_orders_scrollview.clear_widgets()
        answer = super().get_client_data(info)
        if answer == 'server_error':
            Popup(title='Ошибка', content=Label(text='Сервер не работает'), size_hint=(0.8, 0.2)).open()
        elif answer == 'done ':
            self.client_orders_scrollview.height = 180
            self.client_orders_scrollview.add_widget(Label(text='Нет активных заказов' if info == 'orders' else 'Нет шаблонов', color=(0, 0, 0, 1), font_size=(self.height/30)))
        elif answer == 'error login_doesnt_exists':
            Popup(title='Ошибка', content=Label(text='FATAL'), size_hint=(0.8, 0.2)).open()
        else:
            answer = answer.split(' ~ ')
            if answer[0] == 'done':
                new_height = 10 * (len(answer) - 2) + 180 * (len(answer) - 1)
                self.client_orders_scrollview.height = new_height
                if info == 'orders':
                    for i in range(1, len(answer)):
                        order = answer[i].split(' ')
                        order_id = int(order[0])
                        name = order[2]
                        price = order[3]+'₽'
                        description = order[4]
                        start = order[5]
                        finish = order[6]
                        courier = order[7]
                        name = name.replace('_', ' ')
                        self.client_orders_scrollview.add_widget(ClientOrderPreview(order_id, description, name, price, start, finish, courier))
                elif info == 'templates':
                    for i in range(1, len(answer)):
                        template = answer[i].split(' ')
                        name = template[1]
                        price = template[2]
                        description = template[3]
                        start = template[4]
                        finish = template[5]
                        name = name.replace('_', ' ')
                        self.client_orders_scrollview.add_widget(ClientTemplatePreview(name, price, description, start, finish))
            else:
                Popup(title='Ошибка', content=Label(text='FATAL'), size_hint=(0.8, 0.2)).open()

    def show_profile(self):
        path_to_avatar = os.path.join(os.getcwd(), 'src', 'windows', 'profile', 'avatar.jpg')
        path_to_fullname = os.path.join(os.getcwd(), 'src', 'windows', 'profile', 'fullname')
        if not os.path.isfile(path_to_avatar):
            answer = super().get_profile_data()
            if answer == 'server_error':
                Popup(title='Ошибка', content=Label(text='Сервер не работает'), size_hint=(0.8, 0.2)).open()
            else:
                answer = answer.split(' ')
                if answer[0] == 'done':
                    self.user_fullname.text = f'[b]{answer[1]} {answer[2]}[/b]'
                    with open(path_to_fullname, 'w') as file:
                        file.write(f'{answer[1]} {answer[2]}')
                    self.user_avatar.path = path_to_avatar
                elif answer[0] == 'error':
                    if answer[1] == 'fullness_false':
                        Popup(title='Завершить регистрацию', content=Label(text='Заполните профиль\nПрофиль -> Редактировать Данные'), size_hint=(0.9, 0.2)).open()
                    elif answer[1] == 'client_didnt_get_size_correctly':
                        Popup(title='Ошибка', content=Label(text='Ошибка при передаче'), size_hint=(0.8, 0.2)).open()
                    elif answer[1] == 'client_didnt_get_picture_correctly':
                        Popup(title='Ошибка', content=Label(text='Ошибка при передаче'), size_hint=(0.8, 0.2)).open()
                    else:
                        Popup(title='Ошибка', content=Label(text='FATAL'), size_hint=(0.8, 0.2)).open()
                else:
                    Popup(title='Ошибка', content=Label(text='FATAL'), size_hint=(0.8, 0.2)).open()
        else:
            with open(path_to_fullname, 'r') as file:
                data = file.read()
            data = data.split(' ')
            self.user_fullname.text = f'[b]{data[0]} {data[1]}[/b]'
            self.user_avatar.path = path_to_avatar

    def send_new_object_request(self, object):
        fullness = super().get_profile_fullness()
        if fullness == 'done True':
            if (object != 'order' and object != 'template'):
                Popup(title='Ошибка', content=Label(text='FATAL'), size_hint=(0.8, 0.2)).open()
            name = self.new_order_name.text
            price = self.new_order_price.text
            description = self.new_order_description.text
            adress_from = self.new_order_from.text
            adress_to = self.new_order_to.text
            for i in price:
                if i not in '0123456789':
                    Popup(title='Ошибка', content=Label(text='Цена должна состоять только из цифр'), size_hint=(0.8, 0.2)).open()
                    return
            if (name != '' and description != '' and price != '' and adress_from != '' and adress_to != ''):
                name = name.replace(' ', '_')
                description = description.replace(' ', '_')
                adress_from = adress_from.replace(' ', '_')
                adress_to = adress_to.replace(' ', '_')
                answer = super().new_object(object, name, price, description, adress_from, adress_to)
                if answer == 'server_error':
                    Popup(title='Ошибка', content=Label(text='Сервер не работает'), size_hint=(0.8, 0.2)).open()
                else:
                    answer = answer.split(' ')
                    if answer[0] == 'error':
                        Popup(title='Ошибка', content=Label(text='FATAL'), size_hint=(0.8, 0.2)).open()
                    elif answer[0] == 'done':
                        self.new_order_name.text = ''
                        self.new_order_descriprion.text = ''
                        self.new_order_price.text = ''
                        self.new_order_from.text = ''
                        self.new_order_to.text = ''
                        self.client_main_frame.current = 'client_profile'
                    else:
                        Popup(title='Ошибка', content=Label(text='FATAL'), size_hint=(0.8, 0.2)).open()
            else:
                Popup(title='Ошибка', content=Label(text='Заполните все поля'), size_hint=(0.8, 0.2)).open()
        elif fullness == 'done False':
            Popup(title='Ошибка', content=Label(text='Сначала заполните профиль'), size_hint=(0.8, 0.2)).open()
        elif fullness == 'server_error':
            Popup(title='Ошибка', content=Label(text='Сервер не работает'), size_hint=(0.8, 0.2)).open()
        else:
            Popup(title='Ошибка', content=Label(text='FATAL'), size_hint=(0.8, 0.2)).open()