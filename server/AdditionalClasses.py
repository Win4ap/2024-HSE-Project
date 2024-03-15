class Order(object):
    def __init__(self, login, name, cost, description, start, finish, supplier=None):
        self.owner = login
        self.name = name
        self.cost = cost
        self.description = description
        self.start = start
        self.finish = finish
        self.supplier = supplier

    def get_tuple(self) -> tuple:
        return (self.owner, self.name, self.cost, self.description, self.start, self.finish, self.supplier)
