

from typing import Any


text: str = "ballon"
percentage: float = 0.5
fees: int = 100

number: int | float = 10

digits: list[int] = [1, 2, 3, 4, 5]
digitsText: list[Any] = ["one", "two", 3, 4, 5]

table5: tuple[int, int, int, int, int] = (5, 10, 15, 20, 25)
table_5: tuple[int, ...] = (5, 10, 15, 20, 25, 30, 35, 40, 45, 50)

# Custom class as type
class City:
    def __init__(self, name: str, location: int):
        self.name = name
        self.location = location

hampshire = City("hamspshire", 2048593)
city_temp:tuple[City, float] = (hampshire, 25.5)

shipment: dict[str, Any] = {
    "id": 12701,
    "weight": 1.2,
    "content": "wooden table",
    "status": "in transit",
}

def root(num: int | float, exp: float | None = .5) -> float:
    return pow(num, exp)



