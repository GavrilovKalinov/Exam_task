# coding: utf-8
# license: GPLv3
import math

gravitational_constant = 6.67408E-11  # Н·м²/кг² (более точное значение)
max_speed = 1.0E5  # Максимальная скорость для стабильности симуляции
moon_orbit_threshold = 100  # Максимальное расстояние спутника в радиусах планеты

def calculate_force(body, space_objects):
    """
    Вычисляет силу, действующую на тело, с учетом иерархии системы:
    - Спутники учитывают только свою планету
    - Планеты учитывают все звезды и другие планеты
    - Звезды учитывают все другие звезды
    """
    body.Fx = body.Fy = 0.0

    # Для спутников учитываем только гравитацию родительской планеты
    if getattr(body, 'type', None) == 'moon' and hasattr(body, 'parent'):
        parent = body.parent
        dx = parent.x - body.x
        dy = parent.y - body.y
        r = (dx ** 2 + dy ** 2) ** 0.5 + 1E-10  # Добавляем малую величину для избежания деления на 0
        force = gravitational_constant * body.m * parent.m / r ** 2
        body.Fx += force * dx / r
        body.Fy += force * dy / r
        return

    # Для планет и звезд полный расчет гравитации
    for obj in space_objects:
        # Не учитываем влияние самого на себя и спутников на свои планеты
        if (body == obj or
                (getattr(body, 'type', None) == 'moon' and obj == getattr(body, 'parent', None))):
            continue

        dx = obj.x - body.x
        dy = obj.y - body.y
        r = (dx ** 2 + dy ** 2) ** 0.5 + 1E-10  # Защита от деления на 0

        # Для планет игнорируем спутники (кроме своего собственного)
        if (body.type == 'planet' and
                getattr(obj, 'type', None) == 'moon' and
                getattr(obj, 'parent', None) != body):
            continue

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
    """
    Основной цикл пересчета физики системы:
    1. Вычисляем силы для всех объектов
    2. Обновляем их положения
    """
    # Сначала вычисляем все силы
    for body in space_objects:
        calculate_force(body, space_objects)

    # Затем обновляем позиции
    for body in space_objects:
        move_space_object(body, dt)

    # Корректировка спутников
    for body in space_objects:
        if getattr(body, 'type', None) == 'moon' and hasattr(body, 'parent'):
            parent = body.parent
            distance = ((body.x - parent.x) ** 2 + (body.y - parent.y) ** 2) ** 0.5
            if distance > parent.R * 10:  # Если слишком далеко
                angle = math.atan2(body.y - parent.y, body.x - parent.x)
                body.x = parent.x + parent.R * 4 * math.cos(angle)
                body.y = parent.y + parent.R * 4 * math.sin(angle)


if __name__ == "__main__":
    print("This module is not for direct call!")


