from pydantic import BaseModel
from datetime import datetime, timedelta


class Order(BaseModel):
    id: int = None
    owner: str
    name: str
    cost: int
    description: str = None
    start: str
    finish: str
    supplier: str = None
    time: datetime = datetime.now() + timedelta(hours=3)
    fee: int = None

    def get_tuple(self) -> tuple:
        time = f"{self.time.year}/{self.time.month}/{self.time.day} {self.time.hour}:{self.time.minute}"
        return (self.id, self.owner, self.name, self.cost, self.description, self.start, self.finish, self.supplier, time)


class User(BaseModel):
    state: str 
    login: str 
    password: str = None
    name: str = None
    surname: str = None
    phone: str = None