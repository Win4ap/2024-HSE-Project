import os

from kivy.animation import Animation
from kivy.uix.button import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy_garden.mapview.clustered_marker_layer import ClusteredMarkerLayer
from kivy_garden.mapview import MapMarker

from windows.server_logic.server_interaction import ServerLogic

class ColorAnimBase():
    def change_color(self, widget, color):
        animation = Animation(animated_color=color, duration=0.2)
        animation.start(widget)

    def change_color_state(self, first, second, first_state, second_state, first_color, second_color):
        first.state, second.state = first_state, second_state
        self.change_color(first, first_color)
        self.change_color(second, second_color)

class MapExtension(ServerLogic):
    def update_map_markers(self, map_widget, adress_from, adress_to):
        map_widget.center_on(59.956112684067996, 29.915380996738204) # Saint P.
        #map_widget.remove_layer()
        layer = ClusteredMarkerLayer()
        for adress in [adress_from, adress_to]:
            adress = adress.replace(' ', '+')
            answer = super().YandexGeocoderAPI(adress)
            if answer == 'request_error':
                Popup(title='Ошибка', content=Label(text='Bad request'), size_hint=(0.8, 0.2)).open()
                return
            else:
                coordinates = answer['response']['GeoObjectCollection']['featureMember'][-1]['GeoObject']['Point']['pos'].split(' ')
                layer.add_marker(lon=float(coordinates[0]), lat=float(coordinates[1]), cls=MapMarker)
        map_widget.add_widget(layer)

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

class ClientOrderPreview(ButtonBehavior, BoxLayout, MapExtension):
    def __init__(self, order_id, description, name, price, start, finish, courier, time, type, status, root_sm, link_name, link_desc, link_price, link_courier, link_from, link_to, link_button, link_time, link_map):
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
        self.link_map = link_map

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
        super().update_map_markers(self.link_map, self.start, self.finish)
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