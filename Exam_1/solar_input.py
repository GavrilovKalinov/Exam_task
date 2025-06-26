# coding: utf-8
# license: GPLv3

from solar_objects import Star, Planet, Satellite


def read_space_objects_data_from_file(input_filename): #ИСПРАВЛЕНО#
    """Cчитывает данные о космических объектах из файла, создаёт сами объекты
    и вызывает создание их графических образов

    Параметры:

    **input_filename** — имя входного файла
    """

    objects = []
    with open(input_filename) as input_file:
        for line in input_file:
            if len(line.strip()) == 0 or line[0] == '#':
                continue  # пустые строки и строки-комментарии пропускаем
            object_type = line.split()[0].lower()
            if object_type == "star":  #то же самое сделано для планеты
                star = Star()
                parse_star_parameters(line, star)
                objects.append(star)
            elif object_type == "planet":
                planet = Planet()
                parse_planet_parameters(line, planet)
                objects.append(planet)
            elif object_type == "satellite":
                satellite = Satellite()
                parse_satellite_parameters(line, satellite)
                objects.append(satellite)
            else:
                print(f"Unknown space object: {object_type}")

    return objects


def parse_star_parameters(line, star):  #ИСПРАВЛЕНО#
    """Считывает данные о звезде из строки.
    Входная строка должна иметь слеюущий формат:
    Star <радиус в пикселах> <цвет> <масса> <x> <y> <Vx> <Vy>

    Здесь (x, y) — координаты зведы, (Vx, Vy) — скорость.
    Пример строки:
    Star 10 red 1000 1 2 3 4

    Параметры:

    **line** — строка с описание звезды.
    **star** — объект звезды.
    """
    parts = line.split()
    if len(parts) != 8:
        raise ValueError(f"Invalid Star format: expected 8 parts, got {len(parts)}")

    star.R = float(parts[1])  # радиус
    star.color = parts[2]  # цвет
    star.m = float(parts[3])  # масса
    star.x = float(parts[4])  # координата x
    star.y = float(parts[5])  # координата y
    star.Vx = float(parts[6])  # скорость по x
    star.Vy = float(parts[7])  # скорость по y

def parse_planet_parameters(line, planet): #ИСПРАВЛЕНО#
    """Считывает данные о планете из строки.
    Предполагается такая строка:
    Входная строка должна иметь слеюущий формат:
    Planet <радиус в пикселах> <цвет> <масса> <x> <y> <Vx> <Vy>

    Здесь (x, y) — координаты планеты, (Vx, Vy) — скорость.
    Пример строки:
    Planet 10 red 1000 1 2 3 4

    Параметры:

    **line** — строка с описание планеты.
    **planet** — объект планеты.
    """
    parts = line.split()
    if len(parts) != 8:
        raise ValueError(f"Invalid Planet format: expected 8 parts, got {len(parts)}")

    planet.R = float(parts[1])  # радиус
    planet.color = parts[2]  # цвет
    planet.m = float(parts[3])  # масса
    planet.x = float(parts[4])  # координата x
    planet.y = float(parts[5])  # координата y
    planet.Vx = float(parts[6])  # скорость по x
    planet.Vy = float(parts[7])  # скорость по y

def parse_satellite_parameters(line, satellite):  #ДОБАВЛЕНО
    """Считывает данные о звезде из строки.
    Входная строка должна иметь слеюущий формат:
    Satellite <радиус в пикселах> <цвет> <масса> <x> <y> <Vx> <Vy>

    Здесь (x, y) — координаты зведы, (Vx, Vy) — скорость.
    Пример строки:
    Satellite 10 red 1000 1 2 3 4

    Параметры:

    **line** — строка с описание звезды.
    **satellite** — объект звезды.
    """
    parts = line.split()
    if len(parts) != 8:
        raise ValueError(f"Invalid Star format: expected 8 parts, got {len(parts)}")

    satellite.R = float(parts[1])  # радиус
    satellite.color = parts[2]  # цвет
    satellite.m = float(parts[3])  # масса
    satellite.x = float(parts[4])  # координата x
    satellite.y = float(parts[5])  # координата y
    satellite.Vx = float(parts[6])  # скорость по x
    satellite.Vy = float(parts[7])  # скорость по y


def write_space_objects_data_to_file(output_filename, space_objects): #ИСПРАВЛЕНО#
    """Сохраняет данные о космических объектах в файл.
    Строки должны иметь следующий формат:
    Star <радиус в пикселах> <цвет> <масса> <x> <y> <Vx> <Vy>
    Planet <радиус в пикселах> <цвет> <масса> <x> <y> <Vx> <Vy>

    Параметры:

    **output_filename** — имя входного файла
    **space_objects** — список объектов планет и звёзд
    """
    with open(output_filename, 'w') as out_file:
        for obj in space_objects:
            #Формируем строку для записи с помощью f - строки:
            out_file.write(
                f"{obj.type} {obj.R} {obj.color} {obj.m} "  # тип, радиус, цвет, масса
                f"{obj.x} {obj.y} {obj.Vx} {obj.Vy}\n"  # координаты и скорости
            )
    # сделана функция, сохранающая статистику в заданный файл

if __name__ == "__main__":
    print("This module is not for direct call!")