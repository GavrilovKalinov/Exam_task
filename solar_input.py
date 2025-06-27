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
    """Генерирует планеты для звезды с возможными спутниками, избегая столкновений"""
    planets = []
    is_even_orbit = (orbit_num % 2 == 0) if orbit_num is not None else False
    create_moons = (parent_star.color.lower() in ['red', 'yellow']) and is_even_orbit

    for _ in range(count):
        # Генерация планеты с проверкой столкновений
        collision = True
        attempts = 0
        while collision and attempts < 100:
            planet = Planet()
            planet.orbit_num = orbit_num
            planet.R = 8 + random.randint(0, 5)
            planet.color = get_planet_color(parent_star.color)
            planet.m = random.uniform(1E24, 1E26)

            angle = random.uniform(0, 2 * math.pi)
            distance = random.uniform(min_r, max_r)
            planet.x = parent_star.x + distance * math.cos(angle)
            planet.y = parent_star.y + distance * math.sin(angle)

            # Проверка столкновений с другими планетами
            collision = False
            for p in planets:
                dx = planet.x - p.x
                dy = planet.y - p.y
                if (dx ** 2 + dy ** 2) ** 0.5 < (planet.R + p.R) * 10:
                    collision = True
                    break

            attempts += 1

        if attempts >= 100:
            continue
        print(f"Planet generated: x={planet.x}, y={planet.y}, Vx={planet.Vx}, Vy={planet.Vy}")
        # Расчет орбитальной скорости
        orbital_speed = math.sqrt(gravitational_constant * parent_star.m / distance)
        speed_factor = 0.9 + 0.2 * random.random()
        orbital_speed *= speed_factor

        # Направление вращения в зависимости от четности орбиты
        if is_even_orbit:  # Четные орбиты - по часовой стрелке
            planet.Vx = orbital_speed * math.sin(angle)
            planet.Vy = -orbital_speed * math.cos(angle)
        else:  # Нечетные орбиты - против часовой стрелки
            planet.Vx = -orbital_speed * math.sin(angle)
            planet.Vy = orbital_speed * math.cos(angle)

        if create_moons:
            moon = generate_moon(planet)
            if moon:
                planet.add_moon(moon)

        planets.append(planet)

    return planets


def generate_moon(planet):
    """Генерирует спутник для планеты с проверкой безопасного расстояния"""
    if not hasattr(planet, 'R') or planet.R <= 0:
        return None

    moon = Moon(parent_planet=planet)
    moon.R = max(3, int(planet.R * 0.3))
    moon.color = "#888888"
    moon.m = planet.m * 0.01

    # Базовое расстояние (25 радиусов планеты)
    base_distance = planet.R * 25

    # Если у планеты уже есть спутники, увеличиваем расстояние
    if hasattr(planet, 'moons') and planet.moons:
        moon_distance = base_distance + (len(planet.moons) * planet.R * 30)
    else:
        moon_distance = base_distance

    # Генерация позиции с проверкой столкновений
    collision = True
    attempts = 0
    while collision and attempts < 100:
        moon_angle = random.uniform(0, 2 * math.pi)
        moon.x = planet.x + moon_distance * math.cos(moon_angle)
        moon.y = planet.y + moon_distance * math.sin(moon_angle)

        # Проверка столкновений с другими спутниками
        collision = False
        if hasattr(planet, 'moons'):
            for m in planet.moons:
                dx = moon.x - m.x
                dy = moon.y - m.y
                if (dx ** 2 + dy ** 2) ** 0.5 < (moon.R + m.R) * 5:  # Безопасное расстояние
                    collision = True
                    break

        attempts += 1

    if attempts >= 100:
        return None  # Не удалось разместить спутник без столкновений

    # Расчет орбитальной скорости
    try:
        moon_speed = math.sqrt(gravitational_constant * planet.m / moon_distance)
        moon.Vx = planet.Vx - moon_speed * math.sin(moon_angle)
        moon.Vy = planet.Vy + moon_speed * math.cos(moon_angle)
    except (ValueError, ZeroDivisionError):
        moon.Vx = planet.Vx - 1000 * math.sin(moon_angle)
        moon.Vy = planet.Vy + 1000 * math.cos(moon_angle)

    return moon

def get_planet_color(star_color):
    star_color = star_color.lower().strip()

    # Более точные цвета для планет, соответствующие цвету звезды
    color_palettes = {
        "red": [
            "#FF6B6B", "#FF8E8E", "#FFAAAA", "#FFC3C3",
            "#FF5252", "#FF7B7B", "#FF9E9E", "#FFD1D1"
        ],
        "blue": [
            "#6B8CFF", "#8EA7FF", "#AABDFF", "#C3D2FF",
            "#5282FF", "#7B9BFF", "#9EB4FF", "#D1DEFF"
        ],
        "yellow": [
            "#FFE46B", "#FFE88E", "#FFEBAA", "#FFF0C3",
            "#FFDD52", "#FFE37B", "#FFE89E", "#FFF2D1"
        ],
        "green": [
            "#6BFF6B", "#8EFF8E", "#AAFFAA", "#C3FFC3",
            "#52FF52", "#7BFF7B", "#9EFF9E", "#D1FFD1"
        ]
    }

    # Если цвет звезды неизвестен - золотой по умолчанию
    palette = color_palettes.get(star_color, ["#FFD700"])

    # Убедимся, что все цвета начинаются с одного #
    clean_palette = [color.replace("##", "#") for color in palette]

    return random.choice(clean_palette)



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