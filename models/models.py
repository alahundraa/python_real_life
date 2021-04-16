class Human:
    house = None

    def __init__(self, *args, name: str = None, **kwargs):
        self.name = name
        self.satiety = 30
        self.happiness = 100

    def eat(self, volume: int) -> None:
        if volume < 1:
            raise IOError("Incorrect amount of food. Choose from 1 to 30")
        if volume > 30:
            raise IOError("To much amount of food. Choose from 1 to 30")
        if self.house.food_volume >= volume:
            self.house.total_food_eaten += volume
            self.satiety += volume
            self.house.food_volume -= volume
        else:
            raise IOError(
                f"Not able to eat {volume} points of food, because {self.house.food_volume} points are only available.")

    def health_status_is_ok(self) -> bool:
        return self.satiety >= 0 and self.happiness >= 10

    def __str__(self):
        return f"name={self.name}, satiety={self.satiety}, happiness={self.happiness}"


class House:
    def __init__(self):
        self.money_volume = 100
        self.food_volume = 50
        self.dirt = 0
        self.total_money_earned = 0
        self.total_coats_bought = 0
        self.total_food_eaten = 0

    def __str__(self):
        return f"money={self.money_volume}, food={self.food_volume}, dirt={self.dirt}"


class Husband(Human):
    def play_wot(self):
        self.satiety -= 10
        self.happiness += 20

    def go_to_work(self):
        self.satiety -= 10
        self.house.money_volume += 150
        self.house.total_money_earned += 150


class Wife(Human):
    def buy_food(self, volume):
        if not volume % 10 == 0:
            raise IOError("Food volume needs to be divisible by 10")
        if self.house.money_volume < volume:
            raise IOError(
                f"Not enough money to buy {volume} amount of food, because {self.house.money_volume} "
                f"amount of money is only available")
        else:
            self.satiety -= 10
            self.house.food_volume += volume
            self.house.money_volume -= volume

    def buy_coat(self):
        if self.house.money_volume < 350:
            raise IOError(
                f"Not enough money to buy a coat. {self.house.money_volume} are only available. Coat costs 350")
        else:
            self.satiety -= 10
            self.house.money_volume -= 350
            self.house.total_coats_bought += 1
            self.happiness += 60

    def clean(self):
        self.house.dirt -= 100
        if self.house.dirt < 0:
            self.house.dirt = 0
        self.satiety -= 10
