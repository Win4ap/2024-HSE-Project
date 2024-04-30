from kivy.uix.screenmanager import Screen
from kivy.uix.button import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup

from windows.baseclass import ColorAnimBase, ProfileBase
from windows.server_logic.server_interaction import ServerLogic

class ClientOrderPreview(ButtonBehavior, BoxLayout):
    def __init__(self, order_id, description, name, price, start, finish, courier, root_sm, link_name, link_desc, link_price, link_courier, link_from, link_to, link_delete):
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
        self.link_delete = link_delete

    def on_release(self):
        self.root_sm.current = 'client_order_details'
        self.link_delete.order_id = self.order_id
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

class ClientSide(Screen, ColorAnimBase, ProfileBase, ServerLogic):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.client_main_frame.current = 'client_orders'

    def quit(self):
        super().quit()
        self.client_orders_scrollview.clear_widgets()
        self.client_main_frame.current = 'client_orders'
        self.active_orders.animated_color , self.template_orders.animated_color = (217/255, 217/255, 217/255, 0), (217/255, 217/255, 217/255, 0)

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
                        description = description.replace('_', ' ')
                        start = start.replace('_', ' ')
                        finish = finish.replace('_', ' ')
                        self.client_orders_scrollview.add_widget(ClientOrderPreview(order_id, description, name, price, start, finish, courier, self.client_main_frame, self.details_name, self.details_description, self.details_price, self.details_courier, self.details_from, self.details_to, self.details_delete))
                elif info == 'templates':
                    for i in range(1, len(answer)):
                        template = answer[i].split(' ')
                        name = template[1]
                        price = template[2]
                        description = template[3]
                        start = template[4]
                        finish = template[5]
                        name = name.replace('_', ' ')
                        description = description.replace('_', ' ')
                        start = start.replace('_', ' ')
                        finish = finish.replace('_', ' ')
                        self.client_orders_scrollview.add_widget(ClientTemplatePreview(name, price, description, start, finish, self.client_main_frame, self.make_screen_label, self.new_order_name, self.new_order_description, self.new_order_price, self.new_order_from, self.new_order_to))
            else:
                Popup(title='Ошибка', content=Label(text='FATAL'), size_hint=(0.8, 0.2)).open()

    def send_new_object_request(self, object):
        fullness = super().get_profile_fullness()
        if fullness == 'true':
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
                        self.new_order_description.text = ''
                        self.new_order_price.text = ''
                        self.new_order_from.text = ''
                        self.new_order_to.text = ''
                        self.show_profile()
                        self.switch_main_to('client_profile')
                        Popup(title='Успех', content=Label(text='Ваш заказ/шаблон создан'), size_hint=(0.8, 0.2)).open()
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

    def delete_order(self, order_id):
        if order_id > -1:
            Popup(title='Ура', content=Label(text='Типо удалил'), size_hint=(0.8, 0.2)).open()
        else:
            Popup(title='Ошибка', content=Label(text='FATAL'), size_hint=(0.8, 0.2)).open()