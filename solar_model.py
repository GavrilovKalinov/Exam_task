# coding: utf-8
# license: GPLv3
import math
import random

gravitational_constant = 6.67408E-11  # Н·м²/кг² (более точное значение)
max_speed = 1.0E8 # Максимальная скорость для стабильности симуляции
moon_orbit_threshold = 100  # Максимальное расстояние спутника в радиусах планеты


def calculate_force(body, space_objects):
    """Вычисляет силу, действующую на тело."""
    body.Fx = body.Fy = 0.0

    if body.type == 'star':
        return

    for obj in space_objects:
        if obj == body:
            continue

        dx = obj.x - body.x
        dy = obj.y - body.y
        r_squared = dx**2 + dy**2 + 1E-10
        r = math.sqrt(r_squared)

        force = gravitational_constant * body.m * obj.m / r_squared

        if body.type == 'planet':
            if obj.type == 'star' or obj.type == 'planet':
                body.Fx += force * dx / r
                body.Fy += force * dy / r
        elif body.type == 'moon' and obj == body.parent:
            body.Fx += force * dx / r
            body.Fy += force * dy / r

def move_space_object(body, dt):
    """
    Обновляет положение тела с учетом:
    - Ограничения максимальной скорости
    - Корректного численного интегрирования
    """
    # Звезды остаются неподвижными
    if getattr(body, 'type', None) == 'star':
        return

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

    # Проверка столкновений
    check_collisions(space_objects)


def check_collisions(space_objects):
    """Проверяет и обрабатывает столкновения объектов"""
    for i, body1 in enumerate(space_objects):
        for body2 in space_objects[i + 1:]:
            # Пропускаем проверку для звезд (они неподвижны)
            if body1.type == 'star' or body2.type == 'star':
                continue

            # Определяем минимальное безопасное расстояние
            if (body1.type == 'moon' and body2.type == 'moon' and
                    getattr(body1, 'parent', None) == getattr(body2, 'parent', None)):
                # Для спутников одной планеты - более строгая проверка
                min_distance = (body1.R + body2.R) * 3
            elif (body1.type == 'moon' and body2 == getattr(body1, 'parent', None)) or \
                    (body2.type == 'moon' and body1 == getattr(body2, 'parent', None)):
                # Для спутника и его планеты
                min_distance = (body1.R + body2.R) * 10
            else:
                # Для всех остальных случаев
                min_distance = (body1.R + body2.R) * 2

            dx = body1.x - body2.x
            dy = body1.y - body2.y
            distance_squared = dx ** 2 + dy ** 2
            min_distance_squared = min_distance ** 2

            # Если объекты слишком близко (или в одной точке)
            if distance_squared < min_distance_squared:
                # Добавляем защиту от деления на ноль
                if distance_squared == 0:
                    # Если объекты в одной точке, немного раздвигаем их случайным образом
                    correction_factor = min_distance / 2
                    angle = random.uniform(0, 2 * math.pi)
                    correction_x = math.cos(angle) * correction_factor
                    correction_y = math.sin(angle) * correction_factor
                else:
                    # Нормальный случай - объекты близко, но не в одной точке
                    distance = math.sqrt(distance_squared)
                    correction_factor = (min_distance - distance) / 2
                    correction_x = (dx / distance) * correction_factor
                    correction_y = (dy / distance) * correction_factor

                # Применяем коррекцию, учитывая массы объектов
                total_mass = body1.m + body2.m
                if total_mass > 0:
                    body1_ratio = body2.m / total_mass
                    body2_ratio = body1.m / total_mass

                    # Корректируем позиции с учетом масс (более тяжелый объект смещается меньше)
                    body1.x += correction_x * body1_ratio
                    body1.y += correction_y * body1_ratio
                    body2.x -= correction_x * body2_ratio
                    body2.y -= correction_y * body2_ratio
                else:
                    # Если массы нулевые (не должно быть, но на всякий случай)
                    body1.x += correction_x
                    body1.y += correction_y
                    body2.x -= correction_x
                    body2.y -= correction_y

                # Дополнительно корректируем скорости для упругого "отскока"
                if distance_squared > 0:
                    nx = dx / math.sqrt(distance_squared)
                    ny = dy / math.sqrt(distance_squared)

                    # Вычисляем относительную скорость
                    dvx = body1.Vx - body2.Vx
                    dvy = body1.Vy - body2.Vy

                    # Проекция скорости на нормаль
                    velocity_along_normal = dvx * nx + dvy * ny

                    # Если объекты сближаются (а не удаляются)
                    if velocity_along_normal < 0:
                        # Коэффициент упругости (0.5 - неупругий, 1.0 - абсолютно упругий)
                        restitution = 0.8

                        # Импульс отталкивания
                        impulse = -(1 + restitution) * velocity_along_normal
                        impulse /= (1 / body1.m + 1 / body2.m) if (body1.m > 0 and body2.m > 0) else 2

                        # Применяем импульс
                        body1.Vx += impulse * nx / body1.m if body1.m > 0 else 0
                        body1.Vy += impulse * ny / body1.m if body1.m > 0 else 0
                        body2.Vx -= impulse * nx / body2.m if body2.m > 0 else 0
                        body2.Vy -= impulse * ny / body2.m if body2.m > 0 else 0



if __name__ == "__main__":
    print("This module is not for direct call!")

