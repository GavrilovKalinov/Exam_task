# coding: utf-8
# license: GPLv3

"""
Модуль визуализации.
Нигде, кроме этого модуля, не используются экранные координаты объектов.
Функции, создающие графические объекты и перемещающие их на экране, принимают физические координаты
"""
from random import *
import math
from solar_input import find_parent_planet
import random
from random import uniform

header_font = ("Arial", 16, "bold")
"""Шрифт в заголовке"""

window_width = 1500
"""Ширина окна"""

window_height = 900
"""Высота окна"""
scale_factor = 3.3

STAR_COLORS = {
    "red": "#FF3333",
    "blue": "#3333FF",
    "yellow": "#FFFF33",
    "green": "#33FF33"
}

ORBIT_COLORS = {
    "red": "#FF6666",
    "blue": "#6666FF",
    "yellow": "#FFFF66",
    "green": "#66FF66"
}

PLANET_COLORS = {
    "red": "#FFAAAA",
    "blue": "#AAAAFF",
    "yellow": "#FFFFAA",
    "green": "#AAFFAA"
}


def scale_x(x):
    """Преобразует физическую x-координату в экранную."""
    return int(x * scale_factor) + window_width // 2


def scale_y(y):
    """Преобразует физическую y-координату в экранную (с инверсией оси)."""
    return window_height // 2 - int(y * scale_factor)


# Изменить функцию calculate_scale_factor():
def calculate_scale_factor(max_distance):
    global scale_factor
    if max_distance <= 0:
        scale_factor = 1.0
    else:
        # Увеличиваем масштаб, чтобы объекты не вылетали за экран
        scale_factor = 0.8 * min(window_width, window_height) / (2 * max_distance)
        # Ограничиваем минимальный масштаб (чтобы планеты не исчезали)
        scale_factor = max(scale_factor, 0.1)  # Не меньше 0.1


def update_object_position(space, body):
    """Обновление позиции объекта на холсте"""
    if not hasattr(body, 'image') or body.image is None:
        return

    x = scale_x(body.x)
    y = scale_y(body.y)
    r = max(1, body.R)
    print(f"Planet at x={body.x}, y={body.y}, screen_x={x}, screen_y={y}, scale_factor={scale_factor}")
    # Всегда обновляем позицию, даже если объект далеко
    space.coords(body.image, x - r, y - r, x + r, y + r)
    space.tag_raise(body.image)

def draw_orbit(canvas, center, radius, width=1, color=None):
    """Рисует орбиту с улучшенной видимостью"""
    try:
        if not color and hasattr(center, 'color'):
            color = ORBIT_COLORS.get(center.color.lower(), "#FF6600")

        x = scale_x(center.x)
        y = scale_y(center.y)
        r = max(20, int(radius * scale_factor))

        orbit_id = canvas.create_oval(
            x - r, y - r,
            x + r, y + r,
            outline=color,
            width=width,
            dash=(4, 2),
            tags=("orbit", f"orbit_{id(center)}"))
        canvas.lower(orbit_id)
        return orbit_id
    except Exception as e:
        print(f"Ошибка при рисовании орбиты: {str(e)}")
        return None
def create_star_image(space, star):
    """Упрощенная отрисовка звезды без лишних эффектов"""
    try:
        x = scale_x(star.x)
        y = scale_y(star.y)
        r = max(15, star.R)  # Минимальный радиус 15 пикселей

        star.image = space.create_oval(
            x - r, y - r,
            x + r, y + r,
            fill=STAR_COLORS.get(star.color.lower(), "#FF3333"),  # Красный по умолчанию
            outline="",
            tags=("star", "core")
        )
    except Exception as e:
        print(f"Ошибка отрисовки звезды: {e}")

def draw_moon_orbit(space, planet, radius):
    """Рисует орбиту спутника вокруг планеты"""
    try:
        if not hasattr(planet, 'moons') or not planet.moons:
            return  # Не рисуем орбиту, если нет спутников

        x = scale_x(planet.x)
        y = scale_y(planet.y)
        r_pixels = int(radius * scale_factor)

        space.create_oval(
            x - r_pixels, y - r_pixels,
            x + r_pixels, y + r_pixels,
            outline=ORBIT_COLORS.get(planet.color.lower(), "#666666"),
            width=1,
            dash=(2, 2),
            tags=("moon_orbit", f"orbit_{id(planet)}")
        )
    except Exception as e:
        print(f"Ошибка отрисовки орбиты спутника: {e}")

def create_moon_image(space, moon):
    """Отрисовка спутника рядом с планетой"""
    try:
        if not hasattr(moon, 'parent'):
            return

        # Экранные координаты
        x = scale_x(moon.x)
        y = scale_y(moon.y)
        r = max(3, moon.R)

        # Создаём изображение спутника
        moon.image = space.create_oval(
            x - r, y - r,
            x + r, y + r,
            fill="#888888",
            outline="#AAAAAA",
            width=1,
            tags=("moon", f"moon_{id(moon)}")
        )
        space.tag_raise(moon.image)

    except Exception as e:
        print(f"Ошибка отрисовки спутника: {e}")

def create_planet_image(space, planet):
    """Отрисовка планеты с кольцом орбиты спутника (если есть спутники)"""
    try:
        # Проверка координат
        x = scale_x(float(planet.x))
        y = scale_y(float(planet.y))

        # Проверка радиуса
        r = max(1, planet.R)  # Минимальный радиус 1 пиксель

        # Получаем цвет планеты (если не задан — серый по умолчанию)
        color = getattr(planet, 'color', '#AAAAAA')

        # Отрисовка планеты
        planet.image = space.create_oval(
            x - r, y - r,
            x + r, y + r,
            fill=color,  # Используем напрямую цвет планеты
            outline="#333333",
            width=2,
            tags=("planet", f"planet_{id(planet)}")
        )

        # Отрисовка орбиты спутников (если есть)
        if hasattr(planet, 'moons') and planet.moons:
            min_orbit_radius = planet.R * 25
            draw_moon_orbit(space, planet, min_orbit_radius)

    except Exception as e:
        print(f"Ошибка отрисовки планеты: {e}")


if __name__ == "__main__":
    print("This module is not for direct call!")