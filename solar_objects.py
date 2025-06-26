

# coding: utf-8
# license: GPLv3
import random
class CelestialBody:
    """Базовый класс для всех небесных тел"""
    def __init__(self):
        self.m = 0        # Масса (кг)
        self.x = 0        # Координата x (м)
        self.y = 0        # Координата y (м)
        self.Vx = 0       # Скорость по x (м/с)
        self.Vy = 0       # Скорость по y (м/с)
        self.Fx = 0       # Сила по x (Н)
        self.Fy = 0       # Сила по y (Н)
        self.R = 5        # Радиус (пиксели)
        self.color = ""   # Цвет
        self.image = None # Графическое представление
        self.type = ""    # Тип объекта

class Star(CelestialBody):
    """Класс звезды, наследуется от CelestialBody"""
    def __init__(self):
        super().__init__()
        self.type = "star"
        self.color = "red"
        self.R = 20       # Звезды обычно больше планет

class Planet(CelestialBody):
    def __init__(self):
        super().__init__()
        self.type = "planet"
        self.moons = []  # Теперь планета явно содержит свои спутники
        self.name = f"Planet_{random.randint(1000, 9999)}"

    def add_moon(self, moon):
        """Добавляет спутник к планете"""
        moon.parent = self
        self.moons.append(moon)

class Moon(CelestialBody):
    """Класс спутника, наследуется от CelestialBody"""
    def __init__(self, parent_planet=None):
        super().__init__()
        self.type = "moon"
        self.color = "gray"
        self.R = 5       # Спутники меньше планет
        self.parent = parent_planet  # Родительская планета