from pydantic import BaseModel


class Order(BaseModel):
    id: int = None
    owner: str
    name: str
    cost: int
    description: str = None
    start: str
    finish: str
    supplier: str = None

    def get_tuple(self) -> tuple:
        return (self.owner, self.name, self.cost, self.description, self.start, self.finish, self.supplier)


class User(BaseModel):
    state: str 
    login: str 
    password: str = None
    name: str = None
    surname: str = None
    phone: str = None