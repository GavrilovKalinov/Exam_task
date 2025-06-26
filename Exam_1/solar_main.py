# coding: utf-8
# license: GPLv3

import tkinter
from tkinter.filedialog import *
from solar_vis import *
from solar_vis import scale_factor
from solar_model import *
from solar_input import *
from tkinter.filedialog import askopenfilename


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


def execution():
    """Основной цикл выполнения вычислений и обновления экрана."""
    global physical_time, displayed_time, scale_factor

    current_scale = scale_factor
    recalculate_space_objects_positions(space_objects, time_step.get())
    scale_factor = current_scale

    for body in space_objects:
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

    # Сброс состояния симуляции
    perform_execution = False
    space.delete("all")
    space_objects = []

    # Выбор файла
    in_filename = askopenfilename(filetypes=(("Text files", "*.txt"),))
    if not in_filename:
        return

    try:
        # Загрузка объектов из файла
        space_objects = read_space_objects_data_from_file(in_filename)
        if not space_objects:
            print("Файл не содержит объектов")
            return

        # Рассчитываем масштаб
        max_distance = max(
            ((obj.x ** 2 + obj.y ** 2) ** 0.5 for obj in space_objects),
            default=3000
        )
        calculate_scale_factor(max_distance * 1.3)
        print(f"Масштаб установлен: {scale_factor}")

        # Разделяем объекты по типам с защитой от отсутствия атрибута type
        stars = [obj for obj in space_objects if getattr(obj, 'type', None) == 'star']
        planets = [obj for obj in space_objects if getattr(obj, 'type', None) == 'planet']
        moons = [obj for obj in space_objects if getattr(obj, 'type', None) == 'moon']

        # Порядок отрисовки (сначала фоновые элементы, потом объекты)
        # 1. Рисуем орбиты планет вокруг звёзд
        for star in stars:
            for r in [300, 450, 600]:
                draw_orbit(space, star, r, color=ORBIT_COLORS.get(star.color.lower()))

        # 2. Рисуем орбиты спутников вокруг планет
        for planet in planets:
            if hasattr(planet, 'moons') and planet.moons:
                draw_moon_orbit(space, planet, planet.R * 4)

        # 3. Рисуем планеты (они должны быть под спутниками)
        for planet in planets:
            create_planet_image(space, planet)

        # 4. Рисуем спутники (они будут поверх планет)
        for moon in moons:
            create_moon_image(space, moon)

        # 5. Рисуем звёзды (они должны быть поверх всего)
        for star in stars:
            create_star_image(space, star)

        # Обновляем время
        displayed_time.set("0.0 seconds gone")

        # Отладочная информация
        print(f"Загружено: {len(stars)} звёзд, {len(planets)} планет, {len(moons)} спутников")
        print("Цвета звёзд:", [star.color for star in stars])
        print("Цвета планет:", [planet.color for planet in planets])
    except Exception as e:
        print(f"Ошибка при загрузке файла: {str(e)}")
        # Очищаем холст при ошибке
        space.delete("all")
        space_objects = []

def save_file_dialog():
    """Сохранение текущего состояния системы в файл."""
    out_filename = asksaveasfilename(filetypes=(("Text file", ".txt"),))
    if out_filename:
        write_space_objects_data_to_file(out_filename, space_objects)


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