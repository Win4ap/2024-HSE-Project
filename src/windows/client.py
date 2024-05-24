from kivy.uix.screenmanager import Screen
from kivy.uix.label import Label
from kivy.uix.popup import Popup

from windows.baseclass import ColorAnimBase, ProfileBase, ClientOrderPreview, ClientTemplatePreview
from windows.server_logic.server_interaction import ServerLogic

class ClientSide(Screen, ColorAnimBase, ProfileBase, ServerLogic):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.client_main_frame.current = 'client_orders'        

    def on_enter(self, *args):
        self.show_client_data('orders')
        return super().on_enter(*args)

    def quit(self):
        super().quit()
        self.client_orders_scrollview.clear_widgets()
        self.client_main_frame.current = 'client_orders'
        self.active_orders.animated_color, self.template_orders.animated_color = (217/255, 217/255, 217/255, 1), (217/255, 217/255, 217/255, 0)

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
        elif answer == []:
            self.client_orders_scrollview.height = 180
            self.client_orders_scrollview.add_widget(Label(text='Нет активных заказов' if info == 'orders' else 'Нет шаблонов', color=(0, 0, 0, 1), font_size=(self.height/30)))
        elif answer == 'error login_doesnt_exists':
            Popup(title='Ошибка', content=Label(text='FATAL'), size_hint=(0.8, 0.2)).open()
        else:
            new_height = 10 * (len(answer) - 1) + 180 * (len(answer))
            self.client_orders_scrollview.height = new_height
            if info == 'orders':
                for order in answer:
                    order_id = order['id']
                    name = order['name']
                    price = str(order['cost'])+'₽'
                    description = order['description']
                    start = order['start']
                    finish = order['finish']
                    courier = str(order['supplier'])
                    name = name.replace('_', ' ')
                    description = description.replace('_', ' ')
                    start = start.replace('_', ' ')
                    finish = finish.replace('_', ' ')
                    self.client_orders_scrollview.add_widget(ClientOrderPreview(order_id, description, name, price, start, finish, courier, self.client_main_frame, self.details_name, self.details_description, self.details_price, self.details_courier, self.details_from, self.details_to, self.details_button))
            elif info == 'templates':
                for template in answer:
                    name = template['name']
                    price = str(template['cost'])
                    description = template['description']
                    start = template['start']
                    finish = template['finish']
                    name = name.replace('_', ' ')
                    description = description.replace('_', ' ')
                    start = start.replace('_', ' ')
                    finish = finish.replace('_', ' ')
                    self.client_orders_scrollview.add_widget(ClientTemplatePreview(name, price, description, start, finish, self.client_main_frame, self.make_screen_label, self.new_order_name, self.new_order_description, self.new_order_price, self.new_order_from, self.new_order_to))

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
                elif answer == 'true' or isinstance(int(answer), int):
                    self.new_order_name.text = ''
                    self.new_order_description.text = ''
                    self.new_order_price.text = ''
                    self.new_order_from.text = ''
                    self.new_order_to.text = ''
                    self.show_profile()
                    self.show_client_data(object + 's')
                    if object == 'order':
                        self.active_orders.animated_color, self.template_orders.animated_color = (217/255, 217/255, 217/255, 1), (217/255, 217/255, 217/255, 0)
                    else:
                        self.active_orders.animated_color, self.template_orders.animated_color = (217/255, 217/255, 217/255, 0), (217/255, 217/255, 217/255, 1)
                    self.switch_main_to('client_orders')
                    Popup(title='Успех', content=Label(text='Ваш заказ/шаблон создан'), size_hint=(0.8, 0.2)).open()
                else:
                    Popup(title='Ошибка', content=Label(text='FATAL'), size_hint=(0.8, 0.2)).open()
            else:
                Popup(title='Ошибка', content=Label(text='Заполните все поля'), size_hint=(0.8, 0.2)).open()
        elif fullness == 'false':
            Popup(title='Ошибка', content=Label(text='Сначала заполните профиль'), size_hint=(0.8, 0.2)).open()
        elif fullness == 'server_error':
            Popup(title='Ошибка', content=Label(text='Сервер не работает'), size_hint=(0.8, 0.2)).open()
        else:
            Popup(title='Ошибка', content=Label(text='FATAL'), size_hint=(0.8, 0.2)).open()

    def delete_order(self, order_id):
        if order_id > -1:
            answer = super().order_operation(order_id, 'delete')
            if answer == 'server_error':
                Popup(title='Ошибка', content=Label(text='Сервер не работает'), size_hint=(0.8, 0.2)).open()
            elif answer == 'Order not found':
                Popup(title='Ошибка', content=Label(text='Заказ не найден'), size_hint=(0.8, 0.2)).open()
            elif answer == 'true':
                Popup(title='Ошибка', content=Label(text=f'Успешная операция: Удалить'), size_hint=(0.8, 0.2)).open()
                self.show_client_data('orders')
                self.switch_main_to('client_orders')
            else:
                Popup(title='Ошибка', content=Label(text='FATAL'), size_hint=(0.8, 0.2)).open()
        else:
            Popup(title='Ошибка', content=Label(text='FATAL'), size_hint=(0.8, 0.2)).open()