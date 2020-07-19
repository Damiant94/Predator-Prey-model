# Autor: Damian Tułacz
# Program został napisany na potrzeby pracy licencjackiej pt. "Konfrontacja modeli równowagi środowiskowej typu automat komórkowy z modelami typu Lotki-Volterry"
# Program stanowi implementację modelu, który ma za zadanie symulować współistnienie dwóch gatunków (drapieżniki i ofiary) w środowisku.
# Model działa na zasadzie automatu komórkowego, z dyskretną siatką dwuwymiarową oraz dyskretnym czasem. Oblicza on położenie
# każdego osobnika w aktualnym kroku czasowym, a następnie wyświetla informację o ich położeniu na siatce dwuwymiarowej w postaci kwadratów
# o odpowiednich kolorach. Pozwala też na zapisanie do pliku informacji o liczebności zwierząt w poszczególnych momentach.

from tkinter import *
from time import sleep
import numpy as np
from random import shuffle, randint, choice


# tworzenie klas 'ofiara' i 'drapieżnik'
# klasa ofiara posiada aktualne położenie, poprzednie położenie, wiek
# klasa drapieżnik posiada aktualne położenie, poprzednie położenie, wskaźnik głodu, listę ostatnich położeń oraz wiek
class Prey:
    def __init__(self, index, age=1):
        self.index = index
        self.prev_index = ()
        self.age = age


class Predator:
    def __init__(self, index, age=1):
        self.index = index
        self.prev_index = ()
        self.hunger = 0
        self.traces = []
        self.age = age


# Funkcja tworząca początkowe listy osobników obu gatunków
def init_orgs():
    init_preys = []
    init_predators = []
    possible_cells = set()
    for a in range(field_size):
        for b in range(field_size):
            possible_cells.add((a, b))
    for i in range(preys_no):
        xy = choice(tuple(possible_cells))
        prey = Prey(xy, randint(1, preys_born))
        init_preys.append(prey)
        preys_cells[xy] = True
        possible_cells.remove(xy)
    for i in range(predators_no):
        xy = choice(tuple(possible_cells))
        predator = Predator(xy, randint(1, predators_born))
        init_predators.append(predator)
        predators_cells[xy] = True
        possible_cells.remove(xy)
    return init_preys, init_predators


# funkcja rusyjąca kwadrat w zadanym położeniu, o zadanym kolorze, na wcześniej stworzonym tle.
def draw_square(xy):
    background.delete(canvas_squares[xy])
    if preys_cells[xy]:
        color = 'green'
    elif predators_cells[xy]:
        color = 'red'
    else:
        color = 'black'
    y_square = xy[1] * square_size
    x_square = xy[0] * square_size
    canvas_squares[xy] = background.create_rectangle(
        y_square,
        x_square,
        y_square + square_size,
        x_square + square_size,
        fill=color, outline='gray5')


# funkcja rysuje początkową siatkę
def draw_init():
    for x in range(field_size):
        for y in range(field_size):
            if preys_cells[x, y]:
                color = 'green'
            elif predators_cells[x, y]:
                color = 'red'
            else:
                color = 'black'
            y_square = y * square_size
            x_square = x * square_size
            canvas_squares[x, y] = background.create_rectangle(
                y_square,
                x_square,
                y_square + square_size,
                x_square + square_size,
                fill=color, outline='gray5')


# funkcja odpowiedzialna za zmianę położeń drapieżników.
def move_predators():
    shuffle(predators)
    # iteracja po drapieżnikach:
    for predator in predators:
        nearest = predator_vision
        nearest_pos = None
        if predator.hunger >= hunger_hunt:

            # wśród wszystkich ofiar sprawdza, która z nich znajduje się w zasięgu wzroku.
            for checked_prey in preys:
                distance_squared = (predator.index[0] - checked_prey.index[0]) ** 2 + (
                                    predator.index[1] - checked_prey.index[1]) ** 2
                if distance_squared <= predator_vision_squared:
                    distance = distance_squared ** 0.5
                    # wśród tych które znajdują się w zasięgu, sprawdza, która jest najbliżej.
                    if distance <= nearest:
                        nearest = distance
                        nearest_pos = checked_prey

            # tworzy wektor ruchu w kierunku najbliższej ofiary.
            if nearest_pos:
                vector = [0, 0]
                vector[0] += (predator.index[0] - nearest_pos.index[0])
                vector[1] += (predator.index[1] - nearest_pos.index[1])
                vabs = (vector[0] ** 2 + vector[1] ** 2) ** 0.5
                if vabs:
                    vector[0] = vector[0] / vabs
                    vector[1] = vector[1] / vabs
                    # określenie nowego położenia (new_x, new_y)
                    # x
                    if vector[0] > 0.5:
                        x_add = -1
                    elif vector[0] < -0.5:
                        x_add = 1
                    else:
                        x_add = 0
                    # y
                    if vector[1] > 0.5:
                        y_add = -1
                    elif vector[1] < -0.5:
                        y_add = 1
                    else:
                        y_add = 0
                else:
                    x_add = 0
                    y_add = 0

                new_xy = [predator.index[0] + x_add,
                          predator.index[1] + y_add]

            else:
                rand1 = randint(-1, 1)
                if rand1 == 0:
                    rand2 = choice((-1, 1))
                else:
                    rand2 = randint(-1, 1)
                new_xy = [predator.index[0] + rand1,
                          predator.index[1] + rand2]
        else:
            rand1 = randint(-1, 1)
            if rand1 == 0:
                rand2 = choice((-1, 1))
            else:
                rand2 = randint(-1, 1)
            new_xy = [predator.index[0] + rand1,
                      predator.index[1] + rand2]

        # upewnienie się, że nowe położenie nie leży poza siatką:
        new_xy[0] = new_xy[0] % field_size
        new_xy[1] = new_xy[1] % field_size
        new_xy = tuple(new_xy)

        # stworzenie listy, która zawiera wszystkie ślady innych drapieżników:
        all_traces = set()
        for checked_predator in predators:
            if predator != checked_predator:
                for trace in checked_predator.traces:
                    all_traces.add(trace)

        # Jeśli nowe położenie znajduje się w miejscu śladu innego drapieżnika, to zmiana położenia nastąpi w innym
        #   losowym kierunku:

        if new_xy in all_traces:
            possible_cell = set()
            for i in (-1, 0, 1):
                for j in (-1, 0, 1):
                    if i != 0 and j != 0:
                        check = ((predator.index[0] + i) % field_size,
                                 (predator.index[1] + j) % field_size)
                        if check not in all_traces and not preys_cells[check] and not predators_cells[check]:
                            possible_cell.add(check)
            if possible_cell:
                new_xy = choice(tuple(possible_cell))
            else:
                new_xy = predator.index
        else:
            # sprawdzenie, czy miejsce jest zajęte
            if predators_cells[new_xy] or preys_cells[new_xy]:
                new_xy = predator.index

        # zmiany atrybutów drapieżników:
        predator.prev_index = predator.index
        predator.index = new_xy
        predator.traces.append(predator.prev_index)
        predators_cells[predator.prev_index] = False
        draw_square(predator.prev_index)
        predators_cells[predator.index] = True
        draw_square(predator.index)
        if len(predator.traces) >= max_traces:
            predator.traces = predator.traces[1:]

        # zjedzenie ofiary, jeśli znajduje się dostatecznie blisko:
        if nearest_pos and nearest < 2:
            preys.remove(nearest_pos)
            preys_cells[nearest_pos.index] = False
            draw_square(nearest_pos.index)
            # jeśli nastąpiło zjedzenie, głód wraca do wartości 0, jeśli nie, zwiększa się o 1:
            predator.hunger = 0
        else:
            predator.hunger += 1

        # rodzenie potomka:
        if predator.age % predators_born == 0:
            if not predators_cells[predator.prev_index] and not preys_cells[predator.prev_index]:
                predators.append(Predator(predator.prev_index))
                predators_cells[predator.prev_index] = True
                draw_square(predator.prev_index)

        predator.age += 1

    # drapieżniki giną, jeśli ich głód osiągnie określony poziom (hunger_death)
    predators_new = []
    for predator in predators:
        if predator.hunger == hunger_death:
            predators_cells[predator.index] = False
            draw_square(predator.index)
        else:
            predators_new.append(predator)
    return predators_new


# funkcja odpowiedzialna za zmianę położeń ofiar:
def move_preys():
    shuffle(preys)
    # iteracja po ofiarach
    for prey in preys:
        rand1 = randint(-1, 1)
        if rand1 == 0:
            rand2 = choice((-1, 1))
        else:
            rand2 = randint(-1, 1)

        new_xy = [prey.index[0] + rand1,
                  prey.index[1] + rand2]

        # upewnienie się, że nowe położenie nie leży poza siatką:
        new_xy[0] = new_xy[0] % field_size
        new_xy[1] = new_xy[1] % field_size
        new_xy = tuple(new_xy)

        # sprawdzenie, czy miejsce jest zajęte
        if preys_cells[new_xy] or preys_cells[new_xy]:
            new_xy = prey.index

        # zmiany atrybutów ofiar
        prey.prev_index = prey.index
        prey.index = new_xy

        # usuwanie kwadratów, które odpowiadają poprzednim położeniom ofiar
        preys_cells[prey.prev_index] = False
        draw_square(prey.prev_index)
        # rysowanie kwadratów, które odpowiadają aktualnym położeniom ofiar
        preys_cells[prey.index] = True
        draw_square(prey.index)

        # rodzenie się nowych ofiar
        if prey.age % preys_born == 0:
            if not predators_cells[prey.prev_index] and not preys_cells[prey.prev_index]:
                preys.append(Prey(prey.prev_index))
                preys_cells[prey.prev_index] = True
                draw_square(prey.prev_index)

        prey.age += 1

# parametry:

# no_of_generations - ilość kroków czasowych, jakie ma trwać symulacja
# report_time - raz na tyle kroków czasowych jest zapisywana liczba zwierząt do pliku
# speed - tyle razy na sekundę jest wyświetlane nowe położenie osobników
# square_size - wielkość pojedyńczego kwadratu (w pikselach)
# field_size - długość i szerokość siatki (liczba komórek)
# predator_vision - zasięg widzenia drapieżników (promień koła)
# hunger_hunt - ilość kroków czasowych, po których drapieżnik zaczyna zwracać uwagę na ofiary
# hunger_death - ilość kroków czasowych jaką drapieżnik może wytrzymać bez jedzenia
# preys_born - raz na tyle kroków czasowych rodzą się nowe ofiary
# predators_born - raz na tyle kroków czasowych rodzą się nowe drapieżniki
# max_traces - tyle kroków czasowych ostatnich położeń drapieżników jest zapamiętywane

no_of_generations = 2000
report_time = 5
speed = 1000
square_size = 10

field_size = 80
predator_vision = 4
hunger_hunt = 4
hunger_death = 8
preys_born = 31
predators_born = 13
max_traces = 0

predator_vision_squared = predator_vision ** 2

# ile losowo położonych osobników ma zostać dodane (w procentach zapełnienia siatki):
preys_percent = 5
predators_percent = 0.5

# obliczenie ilości osobników:
assert preys_percent + predators_percent <= 100, "Początkowy procent drapieżników i ofiar nie może przekraczać 100"
area = field_size ** 2
preys_no = int(area * preys_percent / 100)
predators_no = int(area * predators_percent / 100)

# tworzenie tła dla siatki:
master = Tk()
background = Canvas(master,
                    background='grey',
                    width=square_size * field_size,
                    height=square_size * field_size,
                    highlightthickness=0)
background.pack()

# utworzenie macierzy, która będzie zawierać rysowane na siatce kwadraty:
canvas_squares = np.zeros((field_size, field_size), dtype=int)

# utworzenie macierzy, która będzie zawierać informacje, czy w danym miejscu znajduje się osobnik:
preys_cells = np.zeros((field_size, field_size), dtype=bool)
predators_cells = np.zeros((field_size, field_size), dtype=bool)

# tworzenie listy ofiar oraz listy drapieżników na podstawie ich początkowej liczby:
preys, predators = init_orgs()
draw_init()
file = open("predators_preys.txt", "a")
file.write("index;predators;preys\n")
index = 1
loops_done = 0
while loops_done < no_of_generations:
    # zliczanie liczebności zwierząt do pliku
    if loops_done % report_time == 0:
        file.write("{};{};{}\n".format(index, len(predators), len(preys)))
        index += 1

    predators = move_predators()
    move_preys()

    background.update()
    sleep(1 / speed)

    loops_done += 1
file.close()

mainloop()
