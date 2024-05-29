import os

from kivy.animation import Animation
from kivy.uix.button import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen

from windows.server_logic.server_interaction import ServerLogic

class ColorAnimBase():
    def change_color(self, widget, color):
        animation = Animation(animated_color=color, duration=0.2)
        animation.start(widget)

    def change_color_state(self, first, second, first_state, second_state, first_color, second_color):
        first.state, second.state = first_state, second_state
        self.change_color(first, first_color)
        self.change_color(second, second_color)

class Message(Label):
    def __init__(self, message, text_pos, width):
        super().__init__()
        self.width = width
        self.height = 95
        self.text = message
        self.text_size = self.size
        self.font_size = self.height/2
        self.valign = 'center'
        self.halign = text_pos
        self.color = (0, 0, 0, 1)
        if text_pos == 'right':
            self.cur_color = (170/255, 170/255, 170/255, 1)


class FullChat(Screen, ServerLogic):
    def __init__(self, chat_name, chat_id):
        super().__init__(name=f'chat_{chat_name}_{chat_id}')
        print(f'chat_{chat_name}_{chat_id}')
        self.chat_name = chat_name
        self.chat_id = chat_id

    def on_enter(self):
        self.fill_chat()

    def go_back(self):
        if super().get_login()[0] == 'client':
            self.parent.current = 'client_chat'
        else:
            self.parent.current = 'delivery_chat'

    def fill_chat(self):
        answer = super().get_messages(self.chat_id)
        if answer == 'server_error':
            Popup(title='Ошибка', content=Label(text='Сервер не работает'), size_hint=(0.8, 0.2)).open()
        else:
            self.chat_scroll.clear_widgets()
            if answer['content'] == []:
                self.chat_scroll.height = 180
                self.chat_scroll.add_widget(Label(text='В чате нет сообщений', color=(0, 0, 0, 1), font_size=(self.height/30)))
            else:
                self.chat_scroll.height = 5 * (len(answer['content']) - 1) + 95 * (len(answer['content']))
                cur_user = super().get_login()[1]
                for message in answer['content']: # TODO: message height based on amount of chars/lines/etc сделать красиво крч
                    self.chat_scroll.add_widget(Message(message['message'], 'right' if cur_user == message['owner'] else 'left', self.chat_scroll.width-40))

class ChatPreview(ButtonBehavior, BoxLayout):
    def __init__(self, chat_id, chat_name, last_message, root_sm):
        super().__init__()
        self.chat_id = chat_id
        self.chat_name = chat_name
        self.last_message = last_message
        self.root_sm = root_sm
        self.cur_chat = FullChat(chat_name, chat_id)
        root_sm.add_widget(self.cur_chat)

    def on_release(self):
        self.root_sm.current = f'chat_{self.chat_name}_{self.chat_id}'
        return super().on_release()

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
        if super().get_login()[0] == 'delivery':
            answer = super().get_rating()
            if answer == 'server_error':
                Popup(title='Ошибка', content=Label(text='Сервер не работает'), size_hint=(0.8, 0.2)).open()
            elif answer == 'Fullness is false':
                pass
            elif answer == 'Login not found':
                Popup(title='Ошибка', content=Label(text='Вашего профиля не существует'), size_hint=(0.8, 0.2)).open()
            else:
                answer = float(answer)
                if answer == 6.0:
                    self.user_rating.text = 'Нет рейтинга'
                else:
                    self.user_rating.text = f'Ваш рейтинг: {round(answer, 1)}'
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

    def fill_scroll(self, scroll, category, root_sm, link_name, link_desc, link_price, link_person, link_from, link_to):
        answer = super().get_archive_orders()
        scroll.clear_widgets()
        data = super().get_login()
        state = data[0]
        if answer == 'server_error':
            Popup(title='Ошибка', content=Label(text='Сервер не работает'), size_hint=(0.8, 0.2)).open()
        elif answer == 'Login not found':
            Popup(title='Ошибка', content=Label(text='Вашего профиля не существует'), size_hint=(0.8, 0.2)).open()
        elif answer == [] or answer == 'Not Found' or answer == 'Fullness is false':
            scroll.height = 180
            scroll.add_widget(Label(text='Нет архивированных заказов' if category == 'archive' else 'Отзывы не требуются', color=(0, 0, 0, 1), font_size=(self.height/30)))
        else:
            count = 0
            for order in answer:
                order_id = order['id']
                name = order['name']
                price = str(order['cost'])+'₽'
                description = order['description']
                start = order['start']
                finish = order['finish']
                if state == 'delivery':
                    person = str(order['owner'])
                else:
                    person = str(order['supplier'])
                name = name.replace('_', ' ')
                description = description.replace('_', ' ')
                start = start.replace('_', ' ')
                finish = finish.replace('_', ' ')
                if category == 'archive':
                    count += 1
                    scroll.add_widget(ArchiveOrder(order_id, description, name, price, start, finish, person, root_sm, link_name, link_desc, link_price, link_person, link_from, link_to))
                elif category == 'review' and order['last_cost'] == None:
                    count += 1
                    scroll.add_widget(PendingReview(order_id, description, name, price, start, finish, person, root_sm, link_name, link_desc, link_price, link_person, link_from, link_to))
            if count != 0:
                new_height = 10 * (count - 1) + 180 * (count)
                scroll.height = new_height
            else:
                scroll.height = 180
                scroll.add_widget(Label(text='Нет архивированных заказов' if category == 'archive' else 'Отзывы не требуются', color=(0, 0, 0, 1), font_size=(self.height/30)))

    def update_chat_list(self, chat_sm, root_sm):
        answer = super().get_user_chats()
        if answer == 'server_error':
            Popup(title='Ошибка', content=Label(text='Сервер не работает'), size_hint=(0.8, 0.2)).open()
        elif isinstance(answer, list):
            chat_sm.clear_widgets()
            if answer == []:
                chat_sm.height = 180
                chat_sm.add_widget(Label(text='Нет активных чатов', color=(0, 0, 0, 1), font_size=(self.height/30)))
            else:
                chat_sm.height = 10 * (len(answer) - 1) + 180 * (len(answer))
                for item in answer:
                    chat_sm.add_widget(ChatPreview(item['id'], item['name'].replace('_', ' '), item['last message'], root_sm))
        else:
            Popup(title='Ошибка', content=Label(text='FATAL'), size_hint=(0.8, 0.2)).open()

    def create_chat(self, second_user, order_name, chat_sm, root_sm):
        if second_user == 'Нет активного курьера':
            Popup(title='Ошибка', content=Label(text='У заказа нет курьера'), size_hint=(0.8, 0.2)).open()
            return
        answer = super().new_chat(second_user, order_name)
        if answer == 'server_error':
            Popup(title='Ошибка', content=Label(text='Сервер не работает'), size_hint=(0.8, 0.2)).open()
        else:
            self.update_chat_list(chat_sm, root_sm)
            root_sm.current = f'chat_{order_name}_{answer}'

class ArchiveOrder(ButtonBehavior, BoxLayout):
    def __init__(self, order_id, description, name, price, start, finish, person, root_sm, link_name, link_desc, link_price, link_person, link_from, link_to):
        super().__init__()
        self.order_id = order_id
        self.description = description
        self.order_name = name
        self.price = price
        self.start = start
        self.finish = finish
        self.person = person
        self.root_sm = root_sm
        self.link_name = link_name
        self.link_desc = link_desc
        self.link_price = link_price
        self.link_person = link_person
        self.link_from = link_from
        self.link_to = link_to

    def on_release(self):
        path_to_login = os.path.join(os.getcwd(), 'src', 'windows', 'server_logic', 'state_login')
        with open(path_to_login, 'r') as file:
            state = (file.read()).split(' ')[0]
        self.root_sm.current = f'{state}_archive_details'
        self.link_name.text = self.order_name
        self.link_desc.text = self.description
        self.link_price.text = self.price
        self.link_from.text = f'Забрать отсюда: {self.start}'
        self.link_to.text = f'Доставить сюда: {self.finish}'
        self.link_person.text = self.person
        return super().on_release()
    
class PendingReview(ArchiveOrder):
    def __init__(self, order_id, description, name, price, start, finish, person, root_sm, link_name, link_desc, link_price, link_person, link_from, link_to):
        super().__init__(order_id, description, name, price, start, finish, person, root_sm, link_name, link_desc, link_price, link_person, link_from, link_to)

    def on_release(self):
        self.root_sm.current = 'client_review_details'
        self.link_name.order_id = self.order_id
        self.link_name.text = self.order_name
        self.link_desc.text = self.description
        self.link_price.text = self.price
        self.link_from.text = f'Забрать отсюда: {self.start}'
        self.link_to.text = f'Доставить сюда: {self.finish}'
        self.link_person.text = self.person

class ClientOrderPreview(ButtonBehavior, BoxLayout):
    def __init__(self, order_id, description, name, price, start, finish, courier, time, type, status, root_sm, link_name, link_desc, link_price, link_courier, link_from, link_to, link_button, link_time):
        super().__init__()
        self.order_id = order_id
        self.description = description
        self.order_name = name
        self.price = price
        self.start = start
        self.finish = finish
        self.courier = courier
        self.time = time
        self.type = type
        self.status = status
        self.root_sm = root_sm
        self.link_name = link_name
        self.link_desc = link_desc
        self.link_price = link_price
        self.link_courier = link_courier
        self.link_from = link_from
        self.link_to = link_to
        self.link_button = link_button
        self.link_time = link_time

    def on_release(self):
        path_to_login = os.path.join(os.getcwd(), 'src', 'windows', 'server_logic', 'state_login')
        with open(path_to_login, 'r') as file:
            state = (file.read()).split(' ')[0]
        self.root_sm.current = f'{state}_order_details'
        self.link_button.order_id = self.order_id
        self.link_button.type = self.type
        self.link_name.text = self.order_name
        self.link_desc.text = self.description
        self.link_price.text = self.price
        self.link_from.text = f'Забрать отсюда: {self.start}'
        self.link_to.text = f'Доставить сюда: {self.finish}'
        self.link_time.text = self.time
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
    
class PopupCodeInput(Popup):
    def __init__(self, callback):
        super(PopupCodeInput, self).__init__()
        self.callback = callback

    def save(self):
        if self.code_field.text == '':
            self.callback('empty')
            self.dismiss()
            return
        for i in self.code_field.text:
            if i not in '0123456789' or len(self.code_field.text) != 4:
                Popup(title='Ошибка', content=Label(text='Код состоит из 4-х цифр'), size_hint=(0.8, 0.2)).open()
                self.callback('empty')
                self.dismiss()
                return
        self.callback(self.code_field.text)
        self.dismiss()