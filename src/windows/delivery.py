from kivy.uix.screenmanager import Screen
from kivy.uix.label import Label
from kivy.uix.popup import Popup

from windows.baseclass import ColorAnimBase, ProfileBase, ClientOrderPreview
from windows.server_logic.server_interaction import ServerLogic

class DeliveryActiveOrderPreview(ClientOrderPreview):
    def __init__(self, order_id, description, name, price, start, finish, courier, root_sm, link_name, link_desc, link_price, link_courier, link_from, link_to, link_button):
        super().__init__(order_id, description, name, price, start, finish, courier, root_sm, link_name, link_desc, link_price, link_courier, link_from, link_to, link_button)

    def on_release(self):
        self.link_button.text = 'Завершить'
        self.link_button.operation = 'complete'
        return super().on_release()

class DeliveryFreeOrderPreview(ClientOrderPreview):
    def __init__(self, **kwargs):
        super(ClientOrderPreview, self).__init__(**kwargs)

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
        elif answer == [] or answer == 'Not Found':
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

    def order_interaction(self, operation):
        print(operation)