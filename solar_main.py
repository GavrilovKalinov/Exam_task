# coding: utf-8
# license: GPLv3

import tkinter
from tkinter.filedialog import *
from solar_vis import *
from solar_vis import scale_factor
from solar_vis import draw_orbit
from solar_vis import draw_orbit
from solar_model import *
from solar_input import *
from tkinter.filedialog import askopenfilename

show_orbits = True  # Глобальная переменная для состояния орбит

perform_execution = False
"""Флаг цикличности выполнения расчёта"""

physical_time = 0
"""Физическое время от начала расчёта."""

displayed_time = None
"""Отображаемое на экране время."""

time_step = None
"""Шаг по времени при моделировании."""

time_speed = None
"""Скорость моделирования."""

space_objects = []
"""Список космических объектов."""

space = None
"""Холст для рисования."""

start_button = None
"""Кнопка запуска/паузы."""
toggle_orbits_button = None
"""Кнопка запуска орбит/выключения орбит."""


def execution():
    """Основной цикл выполнения вычислений и обновления экрана."""
    global physical_time, displayed_time, scale_factor

    current_scale = scale_factor
    recalculate_space_objects_positions(space_objects, time_step.get())
    scale_factor = current_scale

    # Очищаем и перерисовываем все объекты
    space.delete("all")  # Очищаем холст

    # Перерисовываем орбиты
    for star in [obj for obj in space_objects if obj.type == 'star']:
        for r in [900, 1500, 1990]:
            draw_orbit(space, star, r, color=ORBIT_COLORS.get(star.color.lower()))

    # Перерисовываем все объекты
    for body in space_objects:
        if body.type == 'star':
            create_star_image(space, body)
        elif body.type == 'planet':
            create_planet_image(space, body)
            if hasattr(body, 'moons') and body.moons:
                draw_moon_orbit(space, body, body.R * 25)
        elif body.type == 'moon':
            create_moon_image(space, body)

        update_object_position(space, body)

    physical_time += time_step.get()
    displayed_time.set(f"{physical_time:.1f} seconds gone")

    if perform_execution:
        space.after(101 - int(time_speed.get()), execution)

def start_execution():
    """Обработчик запуска симуляции."""
    global perform_execution
    perform_execution = True
    start_button['text'] = "Pause"
    start_button['command'] = stop_execution
    execution()
    print('Started execution...')


def stop_execution():
    """Обработчик паузы симуляции."""
    global perform_execution
    perform_execution = False
    start_button['text'] = "Start"
    start_button['command'] = start_execution
    print('Paused execution.')

def open_file_dialog():
    """Открывает диалог выбора файла и загружает космические объекты"""
    global space_objects, perform_execution, scale_factor

    perform_execution = False
    space.delete("all")
    space_objects = []

    in_filename = askopenfilename(filetypes=(("Text files", "*.txt"),))
    if not in_filename:
        return

    try:
        space_objects = read_space_objects_data_from_file(in_filename)
        if not space_objects:
            print("Файл не содержит объектов")
            return

        # Добавляем спутники в общий список объектов (убрать дублирование)
        all_moons = []
        for planet in [obj for obj in space_objects if getattr(obj, 'type', None) == 'planet']:
            if hasattr(planet, 'moons') and planet.moons:
                all_moons.extend(planet.moons)
        space_objects.extend(all_moons)

        max_distance = max(
            ((obj.x ** 2 + obj.y ** 2) ** 0.5 for obj in space_objects),
            default=3000
        )
        print(f"Max distance before scaling: {max_distance}")
        calculate_scale_factor(max_distance * 1.5)
        print(f"Scale factor: {scale_factor}")

        # Разделяем объекты по типам
        stars = [obj for obj in space_objects if getattr(obj, 'type', None) == 'star']
        planets = [obj for obj in space_objects if getattr(obj, 'type', None) == 'planet']
        moons = [obj for obj in space_objects if getattr(obj, 'type', None) == 'moon']

        # Порядок отрисовки
        for star in stars:
            for r in [900, 1500, 1990]:
                draw_orbit(space, star, r, color=ORBIT_COLORS.get(star.color.lower()))

        for star in stars:
            create_star_image(space, star)

        for planet in planets:
            if hasattr(planet, 'moons') and planet.moons:
                draw_moon_orbit(space, planet, planet.R * 25)

        for planet in planets:
            create_planet_image(space, planet)

        for moon in moons:
            create_moon_image(space, moon)

        displayed_time.set("0.0 seconds gone")
        print(f"Загружено: {len(stars)} звёзд, {len(planets)} планет, {len(moons)} спутников")

    except Exception as e:
        print(f"Ошибка при загрузке файла: {str(e)}")
        space.delete("all")
        space_objects = []

def save_file_dialog():
    """Сохранение текущего состояния системы в файл."""
    out_filename = asksaveasfilename(filetypes=(("Text file", ".txt"),))
    if out_filename:
        write_space_objects_data_to_file(out_filename, space_objects)


def toggle_orbits():
    global show_orbits, toggle_orbits_button

    show_orbits = not show_orbits
    try:
        if show_orbits:
            for orbit in space.find_withtag("orbit"):
                space.itemconfigure(orbit, state="normal")
            for moon_orbit in space.find_withtag("moon_orbit"):
                space.itemconfigure(moon_orbit, state="normal")
            toggle_orbits_button.config(text="Hide Orbits")
        else:
            for orbit in space.find_withtag("orbit"):
                space.itemconfigure(orbit, state="hidden")
            for moon_orbit in space.find_withtag("moon_orbit"):
                space.itemconfigure(moon_orbit, state="hidden")
            toggle_orbits_button.config(text="Show Orbits")
    except Exception as e:
        print(f"Ошибка при переключении орбит: {e}")

def main():
    """Основная функция, создающая интерфейс программы."""
    global physical_time, displayed_time, time_step, time_speed
    global space, start_button, space_objects

    print('Modelling started!')
    physical_time = 0

    root = tkinter.Tk()
    root.title("Solar System Simulator")
    root.geometry("1500x750")

    # Настройка главного окна
    root.grid_rowconfigure(0, weight=1)
    root.grid_rowconfigure(1, weight=0)
    root.grid_columnconfigure(0, weight=1)

    # Холст для отрисовки
    space = tkinter.Canvas(root, bg="black")
    space.grid(row=0, column=0, sticky="nsew")

    # Фрейм для кнопок
    frame = tkinter.Frame(root, height=50, bg="lightgray")
    frame.grid(row=1, column=0, sticky="ew")

    # Кнопка Start/Pause
    start_button = tkinter.Button(frame, text="Start", command=start_execution, width=6)
    start_button.pack(side=tkinter.LEFT, padx=5, pady=5)

    # Поле для ввода шага времени
    time_step = tkinter.DoubleVar(value=1)
    time_step_entry = tkinter.Entry(frame, textvariable=time_step, width=5)
    time_step_entry.pack(side=tkinter.LEFT, padx=5, pady=5)

    # Шкала скорости
    time_speed = tkinter.DoubleVar(value=50)
    scale = tkinter.Scale(frame, variable=time_speed, orient=tkinter.HORIZONTAL,
                          from_=1, to=100, length=150)
    scale.pack(side=tkinter.LEFT, padx=5, pady=5)

    # Кнопка включения/выключения орбит
    toggle_orbits_button = tkinter.Button(frame, text="Hide Orbits", command=toggle_orbits)
    toggle_orbits_button.pack(side=tkinter.LEFT, padx=5, pady=5)

    # Кнопки загрузки/сохранения
    load_file_button = tkinter.Button(frame, text="Open file...", command=open_file_dialog)
    load_file_button.pack(side=tkinter.LEFT, padx=5, pady=5)

    save_file_button = tkinter.Button(frame, text="Save to file...", command=save_file_dialog)
    save_file_button.pack(side=tkinter.LEFT, padx=5, pady=5)

    # Метка времени
    displayed_time = tkinter.StringVar()
    displayed_time.set("0.0 seconds gone")
    time_label = tkinter.Label(frame, textvariable=displayed_time)
    time_label.pack(side=tkinter.RIGHT, padx=10, pady=5)

    root.mainloop()
    print('Modelling finished!')


if __name__ == "__main__":
    main()