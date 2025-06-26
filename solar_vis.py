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
        available_size = min(window_width, window_height) * 1.0  # 50% окна
        scale_factor = available_size / max_distance
    print(f"Масштаб: {scale_factor:.4f} (макс. расстояние={max_distance:.1f})")

def create_star_image(space, star):
    """Упрощенная отрисовка звезды без лишних эффектов"""
    try:
        x = scale_x(star.x)
        y = scale_y(star.y)
        r = max(15, star.R)

        star.image = space.create_oval(
            x - r, y - r,
            x + r, y + r,
            fill=STAR_COLORS.get(star.color.lower(), "#FF3333"),
            outline="",
            tags=("star", "core")
        )
    except Exception as e:
        print(f"Ошибка отрисовки звезды: {e}")


def create_planet_image(space, planet):
    """Отрисовка планеты с кольцом орбиты спутника"""
    try:
        # Проверка координат
        try:
            x = scale_x(float(planet.x))
            y = scale_y(float(planet.y))
        except (TypeError, ValueError):
            print(f"Ошибка координат планеты: x={planet.x}, y={planet.y}")
            return

        # Проверка радиуса
        r = max(1, planet.R)  # Минимальный радиус = 1 пиксель

        # Проверка цвета
        color = getattr(planet, 'color', '').lower()
        fill_color = PLANET_COLORS.get(color, "#D3D3D3")

        # Отрисовка планеты
        planet.image = space.create_oval(
            x - r, y - r,
            x + r, y + r,
            fill=fill_color,
            outline="#333333",
            width=2,
            tags=("planet", f"planet_{id(planet)}")
        )

        # Отрисовка орбиты спутников (если они есть)
        if hasattr(planet, 'moons') and planet.moons:
            min_orbit_radius = planet.R * 2  # Минимальный радиус орбиты
            draw_moon_orbit(space, planet, min_orbit_radius)

    except Exception as e:
        print(f"Ошибка отрисовки планеты: {e}")

def create_moon_image(space, moon):
    """Отрисовка спутника рядом с планетой"""
    try:
        if not hasattr(moon, 'parent'):
            return

        parent = moon.parent
        # Фиксированное расстояние от планеты (в 4 радиуса планеты)
        orbit_radius = parent.R * 4

        # Вычисляем текущий угол на орбите
        angle = math.atan2(moon.y - parent.y, moon.x - parent.x)

        # Обновляем позицию спутника
        moon.x = parent.x + orbit_radius * math.cos(angle)
        moon.y = parent.y + orbit_radius * math.sin(angle)

        # Экранные координаты
        x = scale_x(moon.x)
        y = scale_y(moon.y)
        r = max(3, moon.R)  # Минимальный радиус 3 пикселя

        # Создаем изображение спутника
        moon.image = space.create_oval(
            x - r, y - r,
            x + r, y + r,
            fill="#888888",  # Серый цвет
            outline="#AAAAAA",
            width=1,
            tags=("moon", f"moon_{id(moon)}")
        )

        # Убедимся, что спутник выше орбиты, но ниже планеты
        if hasattr(parent, 'image'):
            space.tag_raise(moon.image, parent.image)

    except Exception as e:
        print(f"Moon drawing error: {e}")

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
            tags="orbit"
        )
        canvas.lower(orbit_id)
        return orbit_id
    except Exception as e:
        print(f"Ошибка при рисовании орбиты: {str(e)}")
        return None


def draw_moon_orbit(space, planet, radius):
    """Рисует орбиту спутника вокруг планеты.

    Параметры:
        space (tkinter.Canvas): Холст для отрисовки.
        planet (Planet): Планета, вокруг которой рисуется орбита.
        radius (float): Физический радиус орбиты (в тех же единицах, что и planet.x, planet.y).
                       Должен быть больше радиуса планеты (рекомендуется planet.R * 3 или больше).
    """
    try:
        # Проверка входных данных
        if not hasattr(planet, 'x') or not hasattr(planet, 'y'):
            raise ValueError("У планеты отсутствуют координаты x или y")

        if not isinstance(radius, (int, float)) or radius <= planet.R * 2:
            radius = planet.R * 2  # Минимальный радиус орбиты = 2 радиуса планеты

        # Масштабирование координат
        x = scale_x(planet.x)
        y = scale_y(planet.y)
        r_pixels = int(radius * scale_factor)  # Радиус в пикселях

        # Проверка, что орбита не меньше планеты
        if r_pixels <= planet.R:
            r_pixels = planet.R * 2  # Делаем орбиту гарантированно больше

        # Рисуем орбиту (пунктирный круг)
        space.create_oval(
            x - r_pixels, y - r_pixels,
            x + r_pixels, y + r_pixels,
            outline=ORBIT_COLORS.get(planet.color.lower(), "#666666"),
            width=1,
            dash=(2, 2),  # Пунктирная линия
            tags=("moon_orbit", f"orbit_{id(planet)}")  # Уникальный тег
        )

    except ValueError as ve:
        print(f"Ошибка в данных: {ve}")
    except Exception as e:
        print(f"Ошибка отрисовки орбиты спутника: {e}")


def update_object_position(space, body):
    """Обновление позиции с учетом смещения для спутников"""
    x = scale_x(body.x)
    y = scale_y(body.y)
    r = body.R

    if getattr(body, 'type', None) == 'moon':
        dx, dy = getattr(body, 'image_offset', (0, 0))
        x += dx
        y += dy

    if (x + r < 0 or x - r > space.winfo_width() or
            y + r < 0 or y - r > space.winfo_height()):
        space.coords(body.image, -100, -100, -100, -100)
    else:
        space.coords(body.image, x - r, y - r, x + r, y + r)


if __name__ == "__main__":
    print("This module is not for direct call!")