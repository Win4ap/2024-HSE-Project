from kivy.uix.screenmanager import Screen
from kivy.uix.label import Label
from kivy.uix.popup import Popup

from windows.baseclass import ColorAnimBase, ProfileBase, ClientOrderPreview
from windows.server_logic.server_interaction import ServerLogic

class DeliveryInProcessOrderPreview(ClientOrderPreview):
    def on_release(self):
        self.link_button.text = 'Завершить'
        self.link_button.operation = 'complete'
        return super().on_release()

class DeliveryFreeOrderPreview(ClientOrderPreview):
    def on_release(self):
        self.link_button.text = 'Взять'
        self.link_button.operation = 'take'
        return super().on_release()
    
class DeliveryActiveOrderPreview(ClientOrderPreview):
    def on_release(self):
        self.link_button.text = 'Взять в работу'
        self.link_button.operation = 'start'
        return super().on_release()
    
class DeliveryAuctionPreview(ClientOrderPreview):
    def on_release(self):
        self.link_button.text = 'Понизить цену'
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
        answer1 = super().get_in_process_orders() if cur == 'down' else super().get_free_orders()
        answer2 = super().get_delivery_orders() if cur == 'down' else super().get_auction_orders()
        if answer1 == 'server_error':
            Popup(title='Ошибка', content=Label(text='Сервер не работает'), size_hint=(0.8, 0.2)).open()
        elif (answer1 == [] or answer1 == 'Not Found' or answer1 == 'Fullness is false') and (answer2 == [] or answer2 == 'Not Found' or answer2 == 'Fullness is false'):
            self.delivery_orders_scrollview.height = 180
            self.delivery_orders_scrollview.add_widget(Label(text='Нет активных заказов' if cur == 'down' else 'Нет свободных заказов', color=(0, 0, 0, 1), font_size=(self.height/30)))
        elif answer1 == 'error login_doesnt_exists':
            Popup(title='Ошибка', content=Label(text='FATAL'), size_hint=(0.8, 0.2)).open()
        else:
            new_height = 0
            if answer1 != 'Not Found':
                new_height += 10 * (len(answer1) - 1) + 180 * len(answer1)
                for order in answer1:
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
                        self.delivery_orders_scrollview.add_widget(DeliveryInProcessOrderPreview(order_id, description, name, price, start, finish, owner, 'in_process_orders', 'Текущий', self.delivery_main_frame, self.details_name, self.details_description, self.details_price, self.details_courier, self.details_from, self.details_to, self.details_button))
                    else:
                        self.delivery_orders_scrollview.add_widget(DeliveryFreeOrderPreview(order_id, description, name, price, start, finish, owner, 'free_orders', 'Свободный', self.delivery_main_frame, self.details_name, self.details_description, self.details_price, self.details_courier, self.details_from, self.details_to, self.details_button))
            if answer2 != 'Not Found':
                new_height += 10 * (len(answer2) - 1) + 180 * len(answer2)
                for order in answer2:
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
                        self.delivery_orders_scrollview.add_widget(DeliveryActiveOrderPreview(order_id, description, name, price, start, finish, owner, 'active_orders', 'Активный', self.delivery_main_frame, self.details_name, self.details_description, self.details_price, self.details_courier, self.details_from, self.details_to, self.details_button))
                    else:
                        self.delivery_orders_scrollview.add_widget(DeliveryAuctionPreview(order_id, description, name, price, start, finish, owner, 'auction_orders', 'Аукцион', self.delivery_main_frame, self.details_name, self.details_description, self.details_price, self.details_courier, self.details_from, self.details_to, self.details_button))
            self.delivery_orders_scrollview.height = new_height

    def order_interaction(self, order_id, operation, type):
        answer = super().order_operation(operation, type, order_id)
        if answer == 'server_error':
            Popup(title='Ошибка', content=Label(text='Сервер не работает'), size_hint=(0.8, 0.2)).open()
        elif answer == 'Login not found':
            Popup(title='Ошибка', content=Label(text='Вашего профиля не существует'), size_hint=(0.8, 0.2)).open()
        elif answer == 'Fullness is false':
            Popup(title='Ошибка', content=Label(text='Заполните профиль'), size_hint=(0.8, 0.2)).open()
        elif answer == 'Order not found':
                Popup(title='Ошибка', content=Label(text='Заказ не найден'), size_hint=(0.8, 0.2)).open()
        elif answer == 'true' or str(order_id) == answer:
            Popup(title='Ошибка', content=Label(text=f'Успешная операция: {self.details_button.text}'), size_hint=(0.8, 0.2)).open()
            super().change_color_state(self.active_orders, self.free_orders, 'down', 'normal', (217/255, 217/255, 217/255, 1), (217/255, 217/255, 217/255, 0))
            self.show_orders()
            self.switch_main_to('delivery_orders')
        else:
            Popup(title='Ошибка', content=Label(text='FATAL'), size_hint=(0.8, 0.2)).open()