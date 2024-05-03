from kivy.uix.screenmanager import Screen
from kivy.uix.label import Label
from kivy.uix.popup import Popup

from windows.baseclass import ColorAnimBase, ProfileBase, ClientOrderPreview
from windows.server_logic.server_interaction import ServerLogic

class DeliveryActiveOrderPreview(ClientOrderPreview):
    def on_release(self):
        self.link_button.text = 'Завершить'
        self.link_button.operation = 'complete'
        return super().on_release()

class DeliveryFreeOrderPreview(ClientOrderPreview):
    def on_release(self):
        self.link_button.text = 'Взять'
        self.link_button.operation = 'take'
        return super().on_release()

class DeliverySide(Screen, ColorAnimBase, ProfileBase, ServerLogic):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.delivery_main_frame.current = 'delivery_orders'

    def on_enter(self, *args):
        self.show_orders()
        return super().on_enter(*args)

    def quit(self):
        super().quit()
        self.delivery_main_frame.current = 'delivery_orders'
        self.active_orders.animated_color, self.free_orders.animated_color = (217/255, 217/255, 217/255, 0), (217/255, 217/255, 217/255, 0)

    def switch_main_to(self, screen):
        if self.delivery_main_frame.current != screen:
            self.delivery_main_frame.current = screen
        if screen == 'delivery_chat':
            self.icon_chat.source, self.icon_list.source, self.icon_user.source = 'img/bold_chat.png', 'img/list.png', 'img/user.png'
        elif screen == 'delivery_orders':
            self.icon_chat.source, self.icon_list.source, self.icon_user.source = 'img/chat.png', 'img/bold_list.png', 'img/user.png'
        elif screen == 'delivery_profile':
            self.icon_chat.source, self.icon_list.source, self.icon_user.source = 'img/chat.png', 'img/list.png', 'img/bold_user.png'

    def show_orders(self):
        cur = self.active_orders.state
        self.delivery_orders_scrollview.clear_widgets()
        answer = super().get_delivery_orders() if cur == 'down' else super().get_free_orders()
        if answer == 'server_error':
            Popup(title='Ошибка', content=Label(text='Сервер не работает'), size_hint=(0.8, 0.2)).open()
        elif answer == [] or answer == 'Not Found' or answer == 'Fullness is false':
            self.delivery_orders_scrollview.height = 180
            self.delivery_orders_scrollview.add_widget(Label(text='Нет активных заказов' if cur == 'down' else 'Нет свободных заказов', color=(0, 0, 0, 1), font_size=(self.height/30)))
        elif answer == 'error login_doesnt_exists':
            Popup(title='Ошибка', content=Label(text='FATAL'), size_hint=(0.8, 0.2)).open()
        else:
            new_height = 10 * (len(answer) - 1) + 180 * (len(answer))
            self.delivery_orders_scrollview.height = new_height
            for order in answer:
                order_id = order['id']
                name = order['name']
                price = str(order['cost'])+'₽'
                description = order['description']
                start = order['start']
                finish = order['finish']
                owner = str(order['owner'])
                name = name.replace('_', ' ')
                description = description.replace('_', ' ')
                start = start.replace('_', ' ')
                finish = finish.replace('_', ' ')
                if cur == 'down':
                    self.delivery_orders_scrollview.add_widget(DeliveryActiveOrderPreview(order_id, description, name, price, start, finish, owner, self.delivery_main_frame, self.details_name, self.details_description, self.details_price, self.details_courier, self.details_from, self.details_to, self.details_button))
                else:
                    self.delivery_orders_scrollview.add_widget(DeliveryFreeOrderPreview(order_id, description, name, price, start, finish, owner, self.delivery_main_frame, self.details_name, self.details_description, self.details_price, self.details_courier, self.details_from, self.details_to, self.details_button))

    def order_interaction(self, order_id, operation):
        answer = super().order_operation(order_id, operation)
        if answer == 'server_error':
            Popup(title='Ошибка', content=Label(text='Сервер не работает'), size_hint=(0.8, 0.2)).open()
        elif answer == 'Login not found':
            Popup(title='Ошибка', content=Label(text='Вашего профиля не существует'), size_hint=(0.8, 0.2)).open()
        elif answer == 'Fullness is false':
            Popup(title='Ошибка', content=Label(text='Заполните профиль'), size_hint=(0.8, 0.2)).open()
        elif answer == 'true':
            Popup(title='Ошибка', content=Label(text=f'Успешная операция: {self.details_button.text}'), size_hint=(0.8, 0.2)).open()
            super().change_color_state(self.active_orders, self.free_orders, 'down', 'normal', (217/255, 217/255, 217/255, 1), (217/255, 217/255, 217/255, 0))
            self.show_orders()
            self.switch_main_to('delivery_orders')
        else:
            Popup(title='Ошибка', content=Label(text='FATAL'), size_hint=(0.8, 0.2)).open()