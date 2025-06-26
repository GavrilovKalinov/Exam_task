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
        available_size = min(window_width, window_height) * 0.5  # 50% окна
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
            min_orbit_radius = planet.R * 4  # Минимальный радиус орбиты
            draw_moon_orbit(space, planet, min_orbit_radius)

    except Exception as e:
        print(f"Ошибка отрисовки планеты: {e}")


def create_moon_image(space, moon):
    """
    Отрисовывает спутник на холсте с гарантией, что его размер будет меньше родительской планеты.

    Параметры:
        space (tkinter.Canvas): Холст для рисования
        moon (Moon): Объект спутника

    Особенности:
        - Размер спутника не превышает 50% размера планеты
        - Минимальный размер - 2 пикселя
        - Автоматическое смещение для визуального разделения
        - Защита от ошибок данных
    """
    try:
        # ===== 1. Проверка входных данных =====
        if not hasattr(moon, 'R') or not isinstance(moon.R, (int, float)):
            moon.R = 3  # Значение по умолчанию

        if not hasattr(moon, 'x') or not hasattr(moon, 'y'):
            print(f"Спутник {id(moon)}: отсутствуют координаты")
            return

        # ===== 2. Контроль размера относительно планеты =====
        parent = getattr(moon, 'parent', None)
        if parent:
            # Ограничиваем размер 30% от планеты (вместо 50% для лучшей визуализации)
            max_allowed_R = max(2, int(parent.R * 0.3))
            moon.R = min(moon.R, max_allowed_R)
        else:
            print(f"Спутник {id(moon)}: не указана родительская планета")
            moon.R = min(moon.R, 5)  # Максимум 5px для спутников без планеты

        # ===== 3. Генерация смещения =====
        if not hasattr(moon, 'image_offset'):
            offset = moon.R * 0.7  # Смещение = 70% радиуса
            angle = random.random() * 2 * math.pi
            moon.image_offset = (
                offset * math.cos(angle),
                offset * math.sin(angle)
            )

        # ===== 4. Масштабирование координат =====
        try:
            dx, dy = moon.image_offset
            x = scale_x(float(moon.x)) + dx
            y = scale_y(float(moon.y)) + dy
        except (TypeError, ValueError) as e:
            print(f"Ошибка координат спутника: {e}")
            return

        # ===== 5. Визуальные настройки =====
        moon_color = getattr(moon, 'color', '#888888')
        outline_color = "#AAAAAA" if moon_color == "#888888" else "#666666"

        # ===== 6. Отрисовка =====
        moon.image = space.create_oval(
            x - moon.R, y - moon.R,
            x + moon.R, y + moon.R,
            fill=moon_color,
            outline=outline_color,
            width=0.5,  # Тонкая обводка
            tags=("moon", "satellite", f"moon_{id(moon)}")
        )

        # Для отладки:
        # print(f"Создан спутник: R={moon.R}, позиция={x},{y}, цвет={moon_color}")

    except Exception as e:
        print(f"Критическая ошибка при отрисовке спутника: {e}")
        raise  # Повторно вызываем исключение для отладки

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
            radius = planet.R * 4  # Минимальный радиус орбиты = 4 радиуса планеты

        # Масштабирование координат
        x = scale_x(planet.x)
        y = scale_y(planet.y)
        r_pixels = int(radius * scale_factor)  # Радиус в пикселях

        # Проверка, что орбита не меньше планеты
        if r_pixels <= planet.R:
            r_pixels = planet.R * 3  # Делаем орбиту гарантированно больше

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