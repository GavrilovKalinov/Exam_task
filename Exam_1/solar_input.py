# coding: utf-8
# license: GPLv3

import math
import random
from solar_objects import Star, Planet, Moon
from solar_model import gravitational_constant

from random import choice

def read_space_objects_data_from_file(input_filename):
    """
    Читает данные о космических объектах из файла.
    Возвращает список объектов системы в правильном порядке:
    [звезды, планеты, спутники]
    """
    objects = []
    star_index = 0  # Индекс текущей звезды (0-3)

    try:
        with open(input_filename, 'r', encoding='utf-8') as input_file:
            for line in input_file:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue

                if line.startswith('Star'):
                    # Обработка звезды
                    star = Star()
                    parse_star_parameters(line, star)
                    objects.append(star)
                    star_index += 1
                    orbit_counter = 0  # Счетчик орбит для текущей звезды

                elif line.startswith('$generate_planets'):
                    # Генерация планет для текущей звезды
                    parts = line.split()
                    if len(parts) < 8:
                        print(f"Ошибка формата строки: {line}")
                        continue

                    try:
                        # Находим звезду по цвету
                        target_color = parts[1].lower()
                        parent_star = next(
                            obj for obj in objects
                            if obj.type == 'star' and obj.color.lower() == target_color
                        )

                        # Генерируем планеты для этой звезды
                        planets = generate_planets(
                            parent_star=parent_star,
                            count=int(parts[2]),
                            min_r=float(parts[6]),
                            max_r=float(parts[7]),
                            star_index=star_index - 1,  # Текущий индекс звезды
                            orbit_num=orbit_counter
                        )
                        objects.extend(planets)
                        orbit_counter += 1

                    except StopIteration:
                        print(f"Ошибка: звезда цвета '{parts[1]}' не найдена")
                    except ValueError as e:
                        print(f"Ошибка обработки строки '{line}': {e}")

        # После загрузки всех данных добавляем спутники в общий список
        all_moons = []
        for planet in [obj for obj in objects if obj.type == 'planet']:
            if hasattr(planet, 'moons') and planet.moons:
                all_moons.extend(planet.moons)

        objects.extend(all_moons)
        return objects

    except FileNotFoundError:
        print(f"Файл не найден: {input_filename}")
        return []
    except Exception as e:
        print(f"Критическая ошибка при чтении файла: {e}")
        return []

def find_parent_planet(moon, space_objects):
    """Находит планету-родителя для спутника"""
    for obj in space_objects:
        if obj.type == 'planet':
            distance = ((moon.x - obj.x)**2 + (moon.y - obj.y)**2)**0.5
            if distance < obj.R * 5:  # Если спутник близко к планете
                return obj
    return None


def generate_planets(parent_star, count, min_r, max_r, star_index=None, orbit_num=None):
    """
    Генерирует планеты для звезды с возможными спутниками

    Параметры:
        parent_star (Star): Родительская звезда
        count (int): Количество планет
        min_r (float): Минимальный радиус орбиты
        max_r (float): Максимальный радиус орбиты
        star_index (int): Индекс звезды (0-3)
        orbit_num (int): Номер орбиты
    """
    planets = []
    is_even_orbit = (orbit_num % 2 == 0) if orbit_num is not None else False

    # Для четных орбит гарантируем минимум 3 планеты
    if is_even_orbit:
        count = max(count, 3)

    for i in range(count):
        try:
            # 1. Создаем планету
            planet = Planet()
            planet.R = 10 + i % 5  # Размер от 10 до 14 пикселей
            planet.color = get_planet_color(parent_star.color)
            planet.m = random.uniform(1E24, 1E26)

            # 2. Позиционирование планеты
            angle = 2 * math.pi * i / count
            distance = random.uniform(min_r, max_r)
            planet.x = parent_star.x + distance * math.cos(angle)
            planet.y = parent_star.y + distance * math.sin(angle)

            # 3. Орбитальная скорость планеты
            orbital_speed = math.sqrt(gravitational_constant * parent_star.m / distance) * 0.8
            planet.Vx = parent_star.Vx - orbital_speed * math.sin(angle)
            planet.Vy = parent_star.Vy + orbital_speed * math.cos(angle)

            # 4. Создание спутника (если условия выполнены)
            if (star_index is not None) and is_even_orbit:
                try:
                    moon = Moon(parent_planet=planet)  # Теперь planet точно определена
                    moon.R = max(2, min(int(planet.R * 0.3), 5))  # 30% от планеты, но не более 5px
                    moon.color = "#888888"
                    moon.m = planet.m * 0.01

                    # Позиция спутника
                    moon_angle = random.random() * 2 * math.pi
                    moon_distance = planet.R * 4
                    moon.x = planet.x + moon_distance * math.cos(moon_angle)
                    moon.y = planet.y + moon_distance * math.sin(moon_angle)

                    # Скорость спутника
                    moon_speed = math.sqrt(gravitational_constant * planet.m / moon_distance) * 1.1
                    moon.Vx = planet.Vx - moon_speed * math.sin(moon_angle)
                    moon.Vy = planet.Vy + moon_speed * math.cos(moon_angle)

                    # Связываем объекты
                    moon.parent = planet
                    planet.moons = [moon]

                    print(f"Создан спутник для планеты R={planet.R}")  # Отладка

                except Exception as moon_error:
                    print(f"Ошибка создания спутника: {moon_error}")

            planets.append(planet)

        except Exception as planet_error:
            print(f"Ошибка создания планеты: {planet_error}")

    return planets

def get_planet_color(star_color):
    star_color = star_color.lower().strip()
    color_map = {
        "red": ["#800000", "#D2691E", "#FF0000", "##FFA07A"],
        "blue": ["#AAAAFF", "#9999FF", "#8888FF", "#7777FF"],
        "yellow": ["#FFFFAA", "#FFFF99", "#FFFF88", "#FFFF77"],
        "green": ["#AAFFAA", "#99FF99", "#88FF88", "#77FF77"]
    }
    return random.choice(color_map.get(star_color, ["#FF8888"]))




def parse_star_parameters(line, star):
    """Считывает данные о звезде из строки."""
    parts = line.split()
    if len(parts) < 8:
        raise ValueError("Недостаточно параметров для звезды")

    star.R = float(parts[1])
    star.color = parts[2].lower()
    star.m = float(parts[3])
    star.x = float(parts[4])
    star.y = float(parts[5])
    star.Vx = float(parts[6])
    star.Vy = float(parts[7])


def parse_planet_parameters(line, planet):
    """Считывает данные о планете из строки."""
    parts = line.split()
    if len(parts) != 8:
        raise ValueError(f"Invalid Planet format: expected 8 parts, got {len(parts)}")

    planet.R = float(parts[1])
    planet.color = parts[2]
    planet.m = float(parts[3])
    planet.x = float(parts[4])
    planet.y = float(parts[5])
    planet.Vx = float(parts[6])
    planet.Vy = float(parts[7])


def write_space_objects_data_to_file(output_filename, space_objects):
    """Сохраняет данные о космических объектах в файл."""
    with open(output_filename, 'w') as out_file:
        for obj in space_objects:
            out_file.write(
                f"{obj.type} {obj.R} {obj.color} {obj.m} "
                f"{obj.x} {obj.y} {obj.Vx} {obj.Vy}\n"
            )


if __name__ == "__main__":
    print("This module is not for direct call!")