import os
from itertools import combinations
from hitman.hitman import HC, HitmanReferee
from pprint import pprint
from typing import *
import subprocess


GridClear = List[List[str]]
Grid = List[List[int]]
PropositionnalVariable = int
Literal = int
Clause = List[Literal]
ClauseBase = List[Clause]
Model = List[Literal]

# Variables globales
## Générales
nb_variables: int = 8  # pour le moment
## Matrice
hauteur_mat: int = 0
largeur_mat: int = 0
taille_mat: int = hauteur_mat * largeur_mat
## Infos plateau
hitman_position: Tuple[int, int]
civil_count: int = 0
guard_count: int = 0
known_cells: Dict[Tuple[int, int], HC] = {}  # Cellules connues/visitées par Hitman
guards_field_of_view: Dict[Tuple[
                               int, int], bool] = {}  # Cellules vues par les gardes | None : Inconnue | True : vue par un garde | False : non vue par un garde
civils_field_of_view: Dict[Tuple[
                               int, int], bool] = {}  # Cellules vues par les civils | None : Inconnue | True : vue par un civil | False : non vue par un civil
danger_zone: Dict[Tuple[int, int], bool] = {}
known_guards: Dict[Tuple[int, int], bool] = {}
## Plateau
clauseBase: List[List[int]] = []
dimacs = ""
history : List[Tuple[Tuple[int,int],HC]] = []


############################################### SETTERS ###############################################
def set_hauteur_mat(h: int) -> NoReturn:
    """ Sets the value of hauteur_mat """
    global hauteur_mat
    hauteur_mat = h


def set_largeur_mat(l: int) -> NoReturn:
    """ Sets the value of largeur_mat """
    global largeur_mat
    largeur_mat = l


def set_civil_count(nb: int) -> NoReturn:
    """ Sets the value of largeur_mat """
    global civil_count
    civil_count = nb


def set_guard_count(nb: int) -> NoReturn:
    """ Sets the value of largeur_mat """
    global guard_count
    guard_count = nb


def generateUnknownCells() -> NoReturn:
    """Generates grid of cells """
    global known_cells
    global guards_field_of_view
    global civils_field_of_view
    for i in range(largeur_mat):
        for j in range(hauteur_mat):
            known_cells[(i, j)] = None
            guards_field_of_view[(i, j)] = None
            civils_field_of_view[(i, j)] = None


############################################### AFFICHAGE ###############################################
def generateGrid(gridContent: Dict[Tuple[int, int], HC]) -> GridClear:
    """ Generates the grid with know information """
    grid: GridClear = []
    for _ in range(hauteur_mat):
        grid.append(["XXX" for _ in range(largeur_mat)])

    for i in range(hauteur_mat):
        for j in range(largeur_mat):
            if (j, i) in gridContent.keys():
                content: HC = gridContent[(j, i)]
                if content == HC.EMPTY:
                    grid[i][j] = "___"
                elif content == HC.CIVIL_E:
                    grid[i][j] = "C-E"
                elif content == HC.CIVIL_W:
                    grid[i][j] = "C-W"
                elif content == HC.CIVIL_N:
                    grid[i][j] = "C-N"
                elif content == HC.CIVIL_S:
                    grid[i][j] = "C-S"
                elif content == HC.GUARD_E:
                    grid[i][j] = "G-E"
                elif content == HC.GUARD_W:
                    grid[i][j] = "G-W"
                elif content == HC.GUARD_N:
                    grid[i][j] = "G-N"
                elif content == HC.GUARD_S:
                    grid[i][j] = "G-S"
                elif content == HC.PIANO_WIRE:
                    grid[i][j] = "WIR"
                elif content == HC.SUIT:
                    grid[i][j] = " S "
                elif content == HC.WALL:
                    grid[i][j] = "WAL"
                elif content == HC.TARGET:
                    grid[i][j] = "TAR"

    grid.reverse()
    return grid


############################################### PARCOURS ###############################################

def checkGuard(position: Tuple[int, int], content: HC) -> NoReturn:
    """ Checks if the content of the cell is a guard """
    global guards_field_of_view,known_guards
    if (content == HC.GUARD_E):
        guards_field_of_view[position] = True
        known_guards[position] = True
        if (position[0] < largeur_mat - 1):
            guards_field_of_view[(position[0] + 1, position[1])] = True
            if (position[0] < largeur_mat - 2):
                guards_field_of_view[(position[0] + 2, position[1])] = True

    elif (content == HC.GUARD_W):
        guards_field_of_view[position] = True
        known_guards[position] = True
        if (position[0] > 0):
            guards_field_of_view[(position[0] - 1, position[1])] = True
            if (position[0] > 1):
                guards_field_of_view[(position[0] - 2, position[1])] = True

    elif (content == HC.GUARD_S):
        guards_field_of_view[position] = True
        known_guards[position] = True
        if (position[1] > 0):
            guards_field_of_view[(position[0], position[1] - 1)] = True
            if (position[1] > 1):
                guards_field_of_view[(position[0], position[1] - 2)] = True
    elif (content == HC.GUARD_N):
        guards_field_of_view[position] = True
        known_guards[position] = True
        if (position[1] < hauteur_mat - 1):
            guards_field_of_view[(position[0], position[1] + 1)] = True
            if (position[1] < hauteur_mat - 2):
                guards_field_of_view[(position[0], position[1] + 2)] = True


def checkCivil(position: Tuple[int, int], content: HC) -> NoReturn:
    """ Checks if the content of the cell is a civil """
    if (content == HC.CIVIL_E):
        civils_field_of_view[position] = True
        if (position[0] < largeur_mat - 1):
            civils_field_of_view[(position[0] + 1, position[1])] = True


    elif (content == HC.CIVIL_W):
        civils_field_of_view[position] = True
        if (position[0] > 0):
            civils_field_of_view[(position[0] - 1, position[1])] = True


    elif (content == HC.CIVIL_S):
        civils_field_of_view[position] = True
        if (position[1] > 0):
            civils_field_of_view[(position[0], position[1] - 1)] = True

    elif (content == HC.CIVIL_N):
        civils_field_of_view[position] = True
        if (position[1] < hauteur_mat - 1):
            civils_field_of_view[(position[0], position[1] + 1)] = True


def getNeighbours(position: Tuple[int, int]) -> List[Tuple[int, int]]:
    """ Gets the neighbours cell of the current Hitman Position"""
    neighbours: List[Tuple[int, int]] = []
    if (position[0] > 0):
        #  and known_cells[(position[0] - 1, position[1])] == None
        neighbours.append((position[0] - 1, position[1]))
    if (position[1] < hauteur_mat - 1):
        #  and known_cells[(position[0] , position[1] +1)] == None
        neighbours.append((position[0], position[1] + 1))
    if (position[1] > 0):
        #  and known_cells[(position[0], position[1] - 1)] == None
        neighbours.append((position[0], position[1] - 1))
    if (position[0] < largeur_mat - 1):
        #  and known_cells[(position[0] + 1, position[1])] == None
        neighbours.append((position[0] + 1, position[1]))
    return neighbours


def lookAt(hr: HitmanReferee, position: Tuple[int, int], orientation: HC, neighbour: Tuple[int, int]) -> dict[
    str, Union[str, int, tuple[int, int], HC, list[tuple[tuple[int, int], HC]]]]:
    if (neighbour[0] == position[0] - 1):
        if (orientation == HC.W):
            return hr.move()
        elif (orientation == HC.S):
            return hr.turn_clockwise()
        elif (orientation == HC.N):
            return hr.turn_anti_clockwise()
        else:
            # à améliorer
            hr.turn_clockwise()
            return hr.turn_clockwise()

    elif (neighbour[0] == position[0] + 1):
        if (orientation == HC.E):
            return hr.move()
        elif (orientation == HC.S):
            return hr.turn_anti_clockwise()
        elif (orientation == HC.N):
            return hr.turn_clockwise()
        else:
            # à améliorer
            hr.turn_clockwise()
            return hr.turn_clockwise()

    elif (neighbour[1] == position[1] - 1):
        if (orientation == HC.S):
            return hr.move()
        elif (orientation == HC.E):
            return hr.turn_clockwise()
        elif (orientation == HC.W):
            return hr.turn_anti_clockwise()
        else:
            # à améliorer
            hr.turn_clockwise()
            return hr.turn_clockwise()
    else:
        if (orientation == HC.N):
            return hr.move()
        elif (orientation == HC.E):
            return hr.turn_anti_clockwise()
        elif (orientation == HC.W):
            return hr.turn_clockwise()
        else:
            # à améliorer
            hr.turn_clockwise()
            return hr.turn_clockwise()


def explore(hr: HitmanReferee,
            status: dict[str, Union[str, int, tuple[int, int], HC, list[tuple[tuple[int, int], HC]]]]) -> NoReturn:
    global known_cells, clauseBase, dimacs, history
    position: Tuple[int, int] = status['position']
    path = []
    last_position = []

    #dimacs = clauses_to_dimacs(clauseBase, 7, header=True)

    while (None in known_cells.values()):
        # Cellule de départ placée à empty
        pprint(status)
        # Vérification des points de pénalité. Si +5, hitman est passé devant un garde
        if (status['is_in_guard_range']):
            guards_field_of_view[position] = True
            danger_zone[position] = True
        # Vérification de la première cellule
        if known_cells[position]==None :  known_cells[position] = HC.EMPTY

        # On récupère la vision

        for cell in status['vision']:
            add_knowledge(cell)
            known_cells[tuple(cell[0])] = HC(cell[1])
            checkGuard(tuple(cell[0]), HC(cell[1]))
            checkCivil(tuple(cell[0]), HC(cell[1]))


        # On récupère l'écoute (mettre à jour guard field of view)
        if (last_position != position):

            ctr = constraints_listener(status['position'], status['hear'])
            clauseBase += ctr
            dimacs += clauses_to_dimacs(ctr, 7, header=False)





        # On essaie de déduire la position d'un, ou plusieurs gardes, si on n'a jamais été dans cet état (position + orientation)
        if (status['position'], status['orientation']) not in history and (guard_count+civil_count>0):
            detectGuards()
            history.append((status['position'], status['orientation']))

        last_position = position

        # Si on connait toutes les cellules, on arrête
        if (None not in known_cells.values()): break

        # Si on n'a pas de trajectoire à effectuer ou que le contenu de la prochaine cellule est connue
        if (len(path) == 0 or known_cells[path[len(path) - 1]] != None):

            # On détermine les voisins
            neighbours = getNeighbours(position)

            # Calcul des cellules inconnues, et de la position elle-même (cas de la position de départ)
            not_visited_tmp = [cell for cell in known_cells.keys() if known_cells[cell] == None and cell != position]
            print(known_cells)
            not_visited = []

            # Tri des cellules accessibles
            for cell in neighbours :
                if(known_cells[cell]==None) : not_visited.append(cell)
            for i in range(len(not_visited_tmp)):
                if not unreachable(not_visited_tmp[i]): not_visited.append(not_visited_tmp[i])

            # Calcul le point le plus proche, non visité

            to_visit = min(not_visited, key=lambda point: (point[0] - position[0]) ** 2 + (point[1] - position[1]) ** 2)
            if (to_visit in neighbours):
                status = lookAt(hr, position, status['orientation'], to_visit)
            else:

                paths = findPaths(position, to_visit, status['orientation'])
                path = paths[0][0]



        else:
            status = lookAt(hr, position, status["orientation"], path[path.index(position) + 1])
            position = status["position"]

            # il faut recalculer le chemin en fct de ce qu'on connait poour diminuer le cout

        print(f"Current path : {path}")
        pprint(generateGrid(known_cells))

        dimacs = clauses_to_dimacs(clauseBase, 7,True)
        # print(dimacs)
        write_dimacs_file(dimacs, "hitman.cnf")
        # print(exec_gophersat("hitman.cnf"))
        rebuild(exec_gophersat("hitman.cnf")[1])
        print("****************************************************************")
    pprint(generateGrid(known_cells))
    print(f"Map explored ? : {hr.send_content(known_cells)}")


def add_knowledge(cell: Tuple[Tuple[int, int], HC]):
    global clauseBase, dimacs,guard_count,civil_count
    if (cell[1] == HC.EMPTY):
        var = cell_to_variable((cell[0][0], cell[0][1]), HC.EMPTY)
        clauseBase += [[var]]
        dimacs+=f"{var} 0\n"
    elif (cell[1] == HC.WALL):
        var = cell_to_variable((cell[0][0], cell[0][1]), HC.WALL)
        clauseBase += [[var]]
        dimacs += f"{var} 0\n"
    elif (cell[1] == HC.TARGET):
        var = cell_to_variable((cell[0][0], cell[0][1]), HC.TARGET)
        clauseBase += [[var]]
        dimacs += f"{var} 0\n"

    elif (cell[1] == HC.SUIT):
        var = cell_to_variable((cell[0][0], cell[0][1]), HC.SUIT)
        clauseBase += [[var]]
        dimacs += f"{var} 0\n"

    elif (cell[1] == HC.PIANO_WIRE):
        var = cell_to_variable((cell[0][0], cell[0][1]), HC.PIANO_WIRE)
        clauseBase += [[var]]
        dimacs += f"{var} 0\n"

    elif (cell[1] in [HC.GUARD_N, HC.GUARD_W, HC.GUARD_E, HC.GUARD_S]):
        var = cell_to_variable((cell[0][0], cell[0][1]), HC.GUARD_N)
        clauseBase += [[var]]
        dimacs += f"{var} 0\n"
        guard_count-=1

    elif (cell[1] in [HC.CIVIL_N, HC.CIVIL_W, HC.CIVIL_E, HC.CIVIL_S]):
        var = cell_to_variable((cell[0][0], cell[0][1]), HC.CIVIL_N)
        clauseBase += [[var]]
        dimacs += f"{var} 0\n"
        civil_count-=1



def unreachable(cell: Tuple[int, int]):
    """ Determines if a cell is unreachable (no known and reachable neighbours)"""
    for neighbour in getNeighbours(cell):
        # print(neighbour)
        if known_cells[neighbour] not in [None, HC.WALL, HC.GUARD_S, HC.GUARD_E, HC.GUARD_N, HC.GUARD_W]:

            return False
    return True


def findPaths(start: Tuple[int, int], end: Tuple[int, int], start_direction: HC):
    """Finds the best path from start to end"""
    paths = []
    explorePaths(start, end, [], paths, start_direction)
    # On retourne le chemin de plus faible coût
    print(len(paths))
    paths.sort(key=lambda x: x[1])

    return paths


def explorePaths(current, end, path, paths, start_direction: HC):  # à améliorer pour éviter de générer trop de chemins
    """Explore possible paths to find the best path"""
    global known_cells
    global guards_field_of_view

    path.append(current)  # Ajouter la cellule au chemin

    if current == end:
        print("*****")
        countMalus = compter_malus(path) + compter_rotations_et_mouvements(path, start_direction)
        print((path, countMalus))
        print("*****")
        if (len(paths) != 0 and countMalus >= min(paths, key=lambda x: x[1])[1]):
            pass
        else:
            paths.append((list(path), countMalus))  # Ajouter une copie du chemin à la liste des chemins
    else:
        # Générer tous les mouvements possibles
        next_moves = generateNextMoves(current)

        # On essaie de commencer par récupérer le chemin le plus court si possible
        next_moves.sort(key=lambda k: (k[0] - end[0]) ** 2 + (k[1] - end[1]) ** 2)

        # Explorer chaque mouvement possible
        for move in next_moves:
            # Si le chemin passe par une cellule à éviter, on ne continue pas sur cette cellule
            # or guards_field_of_view[move]==True il faut faire en sorte d'éviter ces cases
            temp_path = path.copy()
            temp_path.append(move)
            if move in path:  # Vérifier si le mouvement a déjà été exploré
                continue


            # Vérifier si le mouvement est accessible
            elif move != end and (known_cells[move] in [None, HC.WALL, HC.GUARD_S, HC.GUARD_E, HC.GUARD_N,
                                                        HC.GUARD_W] or move in known_guards.keys()):
                continue


            # Si le chemin coûte plus qu'un chemin existant que le cout min des chemins connus, on ne le choisit pas
            # On fait le choix de ne pas prendre les chemins deux fois plus long que le chemin de cout minimal déjà connu
            elif paths != [] and path!=[] and compter_malus(path)+compter_rotations_et_mouvements(path,start_direction) > min(paths, key= lambda x : x[1])[1]:
                continue

            else:
                explorePaths(move, end, path, paths, start_direction)

    # Retirer la dernière position explorée pour revenir en arrière
    path.pop()


def generateNextMoves(current: Tuple[int, int]):
    global largeur_mat
    global hauteur_mat
    x, y = current
    next_moves = []

    # Générer les mouvements possibles : droite, gauche, haut, bas
    if x < largeur_mat - 1:
        next_moves.append((x + 1, y))  # Droite
    if x > 0:
        next_moves.append((x - 1, y))  # Gauche
    if y < hauteur_mat - 1:
        next_moves.append((x, y + 1))  # Haut
    if y > 0:
        next_moves.append((x, y - 1))  # Bas

    return next_moves


def compter_rotations_et_mouvements(chemin, orientation_initiale):
    orientations = [HC.W, HC.S, HC.N, HC.E]
    orientation_actuelle = orientations.index(orientation_initiale)
    nb_rotations = 0
    nb_mouvements = 0

    for i in range(len(chemin) - 1):
        x1, y1 = chemin[i]
        x2, y2 = chemin[i + 1]

        delta_x = x2 - x1
        delta_y = y2 - y1

        if delta_x != 0 or delta_y != 0:
            nb_mouvements += abs(delta_x) + abs(delta_y)

            if delta_x != 0 and delta_y != 0:
                nb_rotations += 2
            else:
                nb_rotations += 1

        orientation_actuelle = (orientation_actuelle + nb_rotations) % 4

    return nb_rotations + nb_mouvements


def ajouter_ligne(file_path, ligne):
    with open(file_path, 'a') as fichier:
        fichier.write(ligne)


def supprimer_derniere_ligne(file_path):
    with open(file_path, "r+", encoding="utf-8") as file:

        file.seek(0, os.SEEK_END)

        pos = file.tell() - 1

        while pos > 0 and file.read(1) != "\n":
            pos -= 1
            file.seek(pos, os.SEEK_SET)

        if pos > 0:
            file.seek(pos, os.SEEK_SET)
            file.truncate()


def detectGuards() -> NoReturn:

    global known_cells, clauseBase, dimacs,guard_count

    for cell in [pos for pos in known_cells.keys() if (known_cells[pos] is None and pos not in known_guards.keys())]:
        col, row = cell[0], cell[1]
        var = cell_to_variable((cell[0], cell[1]), HC.GUARD_N)
        #ajouter_ligne("hitman.cnf", f"-{cell_to_variable((col, row), HC.GUARD_N)} 0\n")
        dimacs = clauses_to_dimacs(clauseBase,7,True)
        write_dimacs_file(dimacs + f"-{var} 0\n","hitman.cnf")
        # Si le solveur retourne faux, cela signifie qu'on peut déduire un garde sur la cellule courante.
        # Le garde peut donc potentiellement regarder la cellule en paramètre. On retourne donc vrai.
        if (not exec_gophersat("hitman.cnf")[0]):
            # On considère que c'est un garde
            print(f"GUARD DEDUCTION IN : {col, row}")
            guard_count -= 1
            known_guards[(col, row)] = True
            define_danger_zone((col, row))
            clauseBase += [[var]]
            #supprimer_derniere_ligne("hitman.cnf")
            #ajouter_ligne("hitman.cnf", f"{cell_to_variable((col, row), HC.GUARD_N)} 0\n")
            dimacs += f"{var} 0\n"
        #else:
            #supprimer_derniere_ligne("hitman.cnf")


def define_danger_zone(cell: Tuple[int, int]) -> NoReturn:
    global danger_zone
    c, r = cell[0], cell[1]

    # calcul des positions visible par le garde
    col_min = max([0, c - 2])
    col_max = min([c + 2, largeur_mat - 1])
    row_min = max([0, r - 2])
    row_max = min([r + 2, hauteur_mat - 1])
    for col in range(col_min, col_max + 1):
        for row in range(row_min, row_max + 1):
            danger_zone[(col, row)] = True


def compter_malus(path):
    malus = 0
    for cell in path:
        if guards_field_of_view[cell]:
            malus += 5
        # Si la cellule a été classée comme dangereuse, on considère un malus
        elif (cell in danger_zone.keys() and danger_zone[cell] == True):
            malus += 5
        # Vérification si la cellule est potentiellement dans la vue d'un garde (utilisation SOLVEUR)
        # elif could_be_in_dangerous_zone(cell) : malus +=5

    return malus


def init_exploration(hauteur: int, largeur: int, nb_guardes: int, nb_civils: int):
    global clauseBase, dimacs
    init_solving(hauteur, largeur, nb_guardes, nb_civils)
    clauseBase = generate_constraints()

    # reset des fichiers (on efface leur contenu)
    f = open('hitman.cnf', 'r+')
    f.truncate(0)
    dimacs = clauses_to_dimacs(clauseBase, 7, True)
    write_dimacs_file(dimacs, "hitman.cnf")


def init_solving(hauteur: int, largeur: int, nb_guardes: int, nb_civils: int):
    global taille_mat

    set_hauteur_mat(hauteur)
    set_largeur_mat(largeur)
    set_guard_count(nb_guardes)
    set_civil_count(nb_civils)
    generateUnknownCells()
    taille_mat = hauteur_mat * largeur_mat


############################################### CONTRAINTES ###############################################


def cell_to_variable(cell: Tuple[int, int], content: HC) -> PropositionnalVariable:
    """Transforme une cellule en variable sous format DIMACS (entier)"""
    if (content == HC.CIVIL_N):
        value = 4
    elif (content == HC.TARGET):
        value = 5
    elif (content == HC.SUIT):
        value = 6
    elif (content == HC.PIANO_WIRE):
        value = 7
    else:
        value = content.value
    #return taille_mat * (value - 1) + cell[1] * hauteur_mat + cell[1] + cell[0] + 1
    return (value-1) * taille_mat + cell[0] + (cell[1]*largeur_mat) + 1

def variable_to_cell(i: int) -> Tuple[int, int, HC]:
    """Transforme une variable en cellule"""
    value = (((i - 1) // taille_mat) + 1)
    if value == 4:
        object = HC.CIVIL_N
    elif value == 5:
        object = HC.TARGET
    elif value == 6:
        object = HC.SUIT
    elif value == 7:
        object = HC.PIANO_WIRE
    else:
        object = HC(((i - 1) // taille_mat) + 1)

    ## return ((i - 1) % hauteur_mat,((i - 1) % taille_mat) // largeur_mat, object)
    i = i - (value - 1) * taille_mat - 1
    return (i % largeur_mat, i // largeur_mat, object)


def at_least_one(variables: List[PropositionnalVariable]) -> Clause:
    clause = variables[:]
    return clause


def unique(variables: List[PropositionnalVariable]) -> ClauseBase:
    kb = []
    for v1, v2 in list(combinations(variables, 2)):
        kb.append([-v1, -v2])
    return kb


# retourne l'ensemble de clause traitant la contrainte : "au moins n variables vraies dans la liste"
def at_least_n(n: int, vars: List[int]) -> List[Clause]:
    clauses = []
    if len(vars)!=0 :
        for c in combinations(vars, len(vars) - (n - 1)):
            clauses.append(list(c))
    return clauses


# retourne l'ensemble de clause traitant la contrainte : "au plus n variables vraies dans la liste"
def at_most_n(n: int, vars: List[int]) -> List[Clause]:
    clauses = []
    varsNeg = [i * -1 for i in vars]
    for c in combinations(varsNeg, n + 1):
        clauses.append(list(c))
    return clauses


# retourne l'ensemble de clause traitant la contrainte : "exactement n variables vraies dans la liste"
def exactly_n(n: int, vars: List[int]) -> List[Clause]:
    if vars == []:
        return []
    if n == 0:
        return at_most_n(0, vars)
    if n == len(vars):
        return at_least_n(n, vars)
    clauses = at_most_n(n, vars)
    clauses += at_least_n(n, vars)
    return clauses


def create_cell_constraints() -> ClauseBase:
    # pas deux objets sur une cellule
    kb = []
    for col in range(largeur_mat):
        for row in range(hauteur_mat):
            list = []
            # On fait la supposition que HC.CIVIL_N représente un civil et HC.GUARD_N un garde
            for var in [HC.EMPTY, HC.SUIT, HC.WALL, HC.TARGET, HC.GUARD_N, HC.CIVIL_N, HC.PIANO_WIRE]:
                list.append(cell_to_variable((col, row), var))
            kb.append(at_least_one(list))
            kb += unique(list)
    return kb


def create_objects_constraints() -> ClauseBase:
    kb = []
    # corde et déguisement
    for obj in [HC.PIANO_WIRE, HC.TARGET, HC.SUIT]:
        list = []
        for row in range(hauteur_mat):
            for col in range(largeur_mat):
                list.append(cell_to_variable((col, row), obj))
        kb.append(at_least_one(list))
        kb += unique(list)
    return kb


def create_npc_constraints(nbGuards: int, nbCivils: int) -> ClauseBase:
    kb = []
    variablesGuard = []
    variablesCivil = []
    for col in range(largeur_mat):
        for row in range(hauteur_mat):
            variablesGuard.append(cell_to_variable((col, row), HC.GUARD_N))
            variablesCivil.append(cell_to_variable((col, row), HC.CIVIL_N))

    kb += exactly_n(nbGuards, variablesGuard)
    kb += exactly_n(nbCivils, variablesCivil)
    return kb


def constraints_listener(position: Tuple[int, int], heard: int) -> ClauseBase:
    """ Ajoute les contraintes liées à l'écoute """
    col, row = position[0], position[1]
    # Calcul de la zone d'écoute (on limite le nombre de variables)
    col_min = max([0, col - 2])
    col_max = min([col + 2, largeur_mat - 1])
    row_min = max([0, row - 2])
    row_max = min([row + 2, hauteur_mat - 1])

    variables = []
    # Nombre de personnes entendues, dont la position n'est pas connue
    really_heard = heard
    # calcul des variables concernées par l'écoute
    for col in range(col_min, col_max + 1):
        for row in range(row_min, row_max + 1):
            # Si la cellule est déjà connue, on l'enlève des variables
            if not (col,row) in known_cells.keys() :
                variables.append(cell_to_variable((col, row), HC.GUARD_N))
                variables.append(cell_to_variable((col, row), HC.CIVIL_N))
            # Si la cellule contient un garde,
            if (col, row) in known_guards.keys(): really_heard -=1


    if (really_heard < 5):
        # Si écoute inférieure à 5, on sait qu'il y en a exactement n
        return exactly_n(heard, variables)
    else:
        # Si écoute d'au moins 5, on sait seulement qu'il y en a au moins 5
        return at_least_n(heard, variables)


def generate_constraints():
    global clauseBase,guard_count,civil_count
    #clauseBase = create_cell_constraints() + create_objects_constraints() + create_npc_constraints(guard_count,civil_count)
    clauseBase = create_cell_constraints() + create_objects_constraints()

    print("constraints generated")
    return clauseBase


def clauses_to_dimacs(clauses: ClauseBase, nb_vars: int, header: bool) -> str:
    file = ""
    if (header):
        file = f"p cnf {nb_vars * taille_mat} {len(clauses)}\n"
    for clause in clauses:
        for lit in clause:
            file += f"{lit} "
        file += "0\n"
    return file


def write_dimacs_file(dimacs: str, filename: str):
    with open(filename, "w", newline="") as cnf:
        cnf.write(dimacs)


def exec_gophersat(filename: str, cmd: str = "gophersat", encoding: str = "utf8") -> Tuple[bool, List[int]]:
    result = subprocess.run([cmd, filename], capture_output=True, check=True, encoding=encoding)
    string = str(result.stdout)
    lines = string.splitlines()
    if lines[1] != "s SATISFIABLE":
        return False, []

    model = lines[2][2:-2].split(" ")

    return True, [int(x) for x in model]


def rebuild(model: Model):
    solved = {}
    for var in model:
        if var > 0:
            cell = variable_to_cell(var)
            solved[(cell[0], cell[1])] = cell[2]

    print("SOLUTION SOLVEUR : ")
    pprint(generateGrid(solved))

