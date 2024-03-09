from kivy.uix.screenmanager import Screen
from kivy.uix.button import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup

from windows.baseclass import ColorAnimBase
from windows.server_logic.server_interaction import ServerLogic

class ClientOrderPreview(ButtonBehavior, BoxLayout):
    def __init__(self, order_id, description, name, price, courier):
        super().__init__()
        self.order_id = order_id
        self.description = description
        self.order_name = name
        self.price = price
        self.courier = courier

class ClientTemplatePreview(ButtonBehavior, BoxLayout):
    def __init__(self, name, price, description):
        super().__init__()
        self.template_name = name
        self.price = price
        self.description = description

class ClientSide(Screen, ColorAnimBase, ServerLogic):
    def show_client_data(self, info):
        if (info != 'orders' and info != 'templates'):
            Popup(title='Ошибка', content=Label(text='FATAL'), size_hint=(0.8, 0.2)).open()
        self.client_orders_scrollview.clear_widgets()
        answer = super().get_client_data(info)
        if answer == 'server_error':
            Popup(title='Ошибка', content=Label(text='Сервер не работает'), size_hint=(0.8, 0.2)).open()
        if answer == 'done ':
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
                        courier = order[1] # пока вместо курьера — логин пользователя
                        name = order[2]
                        price = order[3]+'₽'
                        description = order[4]
                        self.client_orders_scrollview.add_widget(ClientOrderPreview(order_id, description, name, price, courier))
                elif info == 'templates':
                    for i in range(1, len(answer)):
                        template = answer[i].split(' ')
                        name = template[1]
                        price = template[2]
                        description = template[3]
                        self.client_orders_scrollview.add_widget(ClientTemplatePreview(name, price, description))
            else:
                Popup(title='Ошибка', content=Label(text='FATAL'), size_hint=(0.8, 0.2)).open()
