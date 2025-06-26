# coding: utf-8
# license: GPLv3
import math

gravitational_constant = 6.67408E-11  # Н·м²/кг² (более точное значение)
max_speed = 1.0E5  # Максимальная скорость для стабильности симуляции
moon_orbit_threshold = 100  # Максимальное расстояние спутника в радиусах планеты

def calculate_force(body, space_objects):
    """Вычисляет силу, действующую на тело."""
    body.Fx = body.Fy = 0.0

    # Для спутников учитываем только гравитацию родительской планеты
    if getattr(body, 'type', None) == 'moon' and hasattr(body, 'parent'):
        parent = body.parent
        distance = ((body.x - parent.x) ** 2 + (body.y - parent.y) ** 2) ** 0.5
        target_distance = parent.R * 4
        dx = parent.x - body.x
        dy = parent.y - body.y
        r = (dx ** 2 + dy ** 2) ** 0.5 + 1E-10
        force = gravitational_constant * body.m * parent.m / r ** 2
        body.Fx += force * dx / r
        body.Fy += force * dy / r
        return

    # Для планет и звезд полный расчет гравитации
    for obj in space_objects:
        if body == obj:
            continue
        dx = obj.x - body.x
        dy = obj.y - body.y
        r = (dx ** 2 + dy ** 2) ** 0.5 + 1E-10
        force = gravitational_constant * body.m * obj.m / r ** 2
        body.Fx += force * dx / r
        body.Fy += force * dy / r

def move_space_object(body, dt):
    """
    Обновляет положение тела с учетом:
    - Ограничения максимальной скорости
    - Корректного численного интегрирования
    """
    # Вычисляем ускорение
    ax = body.Fx / (body.m + 1E-10)  # Защита от деления на 0
    ay = body.Fy / (body.m + 1E-10)

    # Обновляем скорость (метод Эйлера)
    body.Vx += ax * dt
    body.Vy += ay * dt

    # Ограничение скорости для стабильности
    speed = (body.Vx ** 2 + body.Vy ** 2) ** 0.5
    if speed > max_speed:
        body.Vx = body.Vx * max_speed / speed
        body.Vy = body.Vy * max_speed / speed

    # Обновляем позицию
    body.x += body.Vx * dt
    body.y += body.Vy * dt

def recalculate_space_objects_positions(space_objects, dt):
    """Основной цикл пересчета физики системы"""
    # Вычисляем все силы
    for body in space_objects:
        calculate_force(body, space_objects)

    # Обновляем позиции
    for body in space_objects:
        move_space_object(body, dt)

    # Корректировка спутников - фиксируем их на орбитах
    for body in space_objects:
        if getattr(body, 'type', None) == 'moon' and hasattr(body, 'parent'):
            parent = body.parent
            angle = math.atan2(body.y - parent.y, body.x - parent.x)
            target_distance = parent.R * 4  # Фиксированное расстояние

            # Обновляем позицию спутника
            body.x = parent.x + target_distance * math.cos(angle)
            body.y = parent.y + target_distance * math.sin(angle)

            # Корректируем скорость для круговой орбиты
            orbital_speed = math.sqrt(gravitational_constant * parent.m / target_distance)
            body.Vx = parent.Vx - orbital_speed * math.sin(angle)
            body.Vy = parent.Vy + orbital_speed * math.cos(angle)

if __name__ == "__main__":
    print("This module is not for direct call!")


