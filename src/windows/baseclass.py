import os

from kivy.animation import Animation
from kivy.uix.button import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.uix.label import Label

from windows.server_logic.server_interaction import ServerLogic

class ColorAnimBase():
    def change_color(self, widget, color):
        animation = Animation(animated_color=color, duration=0.2)
        animation.start(widget)

    def change_color_state(self, first, second, first_state, second_state, first_color, second_color):
        first.state, second.state = first_state, second_state
        self.change_color(first, first_color)
        self.change_color(second, second_color)

class ProfileBase(ServerLogic):
    def quit(self):
        path_to_login = os.path.join(os.getcwd(), 'src', 'windows', 'server_logic', 'state_login')
        path_to_fullname = os.path.join(os.getcwd(), 'src', 'windows', 'profile', 'fullname')
        path_to_avatar = os.path.join(os.getcwd(), 'src', 'windows', 'profile', 'avatar.jpg')
        path_to_no_avatar = os.path.join(os.getcwd(), 'src', 'windows', 'profile', 'no_avatar.png')
        with open(path_to_login, 'wb'):
            pass
        with open(path_to_fullname, 'wb'):
            pass
        if os.path.isfile(path_to_avatar):
            os.remove(path_to_avatar)
        self.manager.transition.direction = 'down'
        self.manager.current = 'auth'
        self.icon_chat.source, self.icon_list.source, self.icon_user.source = 'img/chat.png', 'img/bold_list.png', 'img/user.png'
        self.user_fullname.text = '[b]Неизвестно[/b]'
        self.user_avatar.path = path_to_no_avatar

    def show_profile(self):
        path_to_avatar = os.path.join(os.getcwd(), 'src', 'windows', 'profile', 'avatar.jpg')
        path_to_fullname = os.path.join(os.getcwd(), 'src', 'windows', 'profile', 'fullname')
        if not os.path.isfile(path_to_avatar):
            answer = super().get_profile_data()
            if answer == 'server_error':
                Popup(title='Ошибка', content=Label(text='Сервер не работает'), size_hint=(0.8, 0.2)).open()
            elif answer == 'Not Found':
                Popup(title='Завершить регистрацию', content=Label(text='Заполните профиль\nПрофиль -> Редактировать данные'), size_hint=(0.9, 0.2)).open()
            else:
                self.user_fullname.text = f'[b]{answer['name']} {answer['surname']}[/b]'
                with open(path_to_fullname, 'w') as file:
                    file.write(f'{answer['name']} {answer['surname']}')
                self.user_avatar.path = path_to_avatar
        else:
            with open(path_to_fullname, 'r') as file:
                data = file.read()
            data = data.split(' ')
            self.user_fullname.text = f'[b]{data[0]} {data[1]}[/b]'
            self.user_avatar.path = path_to_avatar

    def fill_archive(self, archive):
        print('я тёма')

class ClientOrderPreview(ButtonBehavior, BoxLayout):
    def __init__(self, order_id, description, name, price, start, finish, courier, root_sm, link_name, link_desc, link_price, link_courier, link_from, link_to, link_button):
        super().__init__()
        self.order_id = order_id
        self.description = description
        self.order_name = name
        self.price = price
        self.start = start
        self.finish = finish
        self.courier = courier
        self.root_sm = root_sm
        self.link_name = link_name
        self.link_desc = link_desc
        self.link_price = link_price
        self.link_courier = link_courier
        self.link_from = link_from
        self.link_to = link_to
        self.link_button = link_button

    def on_release(self):
        path_to_login = os.path.join(os.getcwd(), 'src', 'windows', 'server_logic', 'state_login')
        with open(path_to_login, 'r') as file:
            state = (file.read()).split(' ')[0]
        self.root_sm.current = f'{state}_order_details'
        self.link_button.order_id = self.order_id
        self.link_name.text = self.order_name
        self.link_desc.text = self.description
        self.link_price.text = self.price
        self.link_from.text = f'Забрать отсюда: {self.start}'
        self.link_to.text = f'Доставить сюда: {self.finish}'
        if self.courier == 'None':
            self.link_courier.text = 'Нет активного курьера'
        else:
            self.link_courier.text = self.courier
        return super().on_release()
    
class ClientTemplatePreview(ButtonBehavior, BoxLayout):
    def __init__(self, name, price, description, start, finish, root_sm, link_label, link_name, link_desc, link_price, link_from, link_to):
        super().__init__()
        self.template_name = name
        self.price = price
        self.description = description
        self.start = start
        self.finish = finish
        self.root_sm = root_sm
        self.link_label = link_label
        self.link_name = link_name
        self.link_desc = link_desc
        self.link_price = link_price
        self.link_from = link_from
        self.link_to = link_to

    def on_release(self):
        self.root_sm.current = 'client_make_new_object'
        self.link_label.text = 'Создать заказ'
        self.link_name.text = self.template_name
        self.link_desc.text = self.description
        self.link_price.text = self.price
        self.link_from.text = self.start
        self.link_to.text = self.finish
        return super().on_release()