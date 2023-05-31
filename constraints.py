from itertools import combinations
from hitman.hitman import HC, HitmanReferee, complete_map_example
from pprint import pprint
from typing import *


GridClear = List[List[str]]
Grid = List[List[int]]
PropositionnalVariable = int
Literal = int
Clause = List[Literal]
ClauseBase = List[Clause]
Model = List[Literal]

# Variables globales
## Générales
nb_variables : int = 8 # pour le moment
## Matrice
hauteur_mat : int = 0
largeur_mat : int = 0
taille_mat : int = hauteur_mat * largeur_mat
## Infos plateau
hitman_position : Tuple[int,int]
civil_count : int = 0
guard_count : int = 0
known_cells : Dict[Tuple[int,int],HC] = {} # Cellules connues/visitées par Hitman
guards_field_of_view : Dict[Tuple[int,int],bool] = {} # Cellules vues par les gardes | None : Inconnue | True : vue par un garde | False : non vue par un garde
civils_field_of_view : Dict[Tuple[int,int],bool] = {} # Cellules vues par les civils | None : Inconnue | True : vue par un civil | False : non vue par un civil
## Plateau







############################################### SETTERS ###############################################
def set_hauteur_mat(h : int) -> NoReturn :
    """ Sets the value of hauteur_mat """
    global hauteur_mat
    hauteur_mat = h

def set_largeur_mat(l : int) -> NoReturn:
    """ Sets the value of largeur_mat """
    global largeur_mat
    largeur_mat = l

def set_civil_count(nb : int) -> NoReturn:
    """ Sets the value of largeur_mat """
    global civil_count
    civil_count = nb

def set_guard_count(nb : int) -> NoReturn:
    """ Sets the value of largeur_mat """
    global guard_count
    guard_count = nb

def generateUnknownCells() -> NoReturn :
    """Generates grid of cells """
    global known_cells
    global guards_field_of_view
    global civils_field_of_view
    for i in range(largeur_mat):
        for j in range(hauteur_mat):
            known_cells[(i,j)] = None
            guards_field_of_view[(i,j)] = None
            civils_field_of_view[(i,j)] = None

############################################### AFFICHAGE ###############################################
def generateGrid() -> GridClear :
    """ Generates the grid with know information """
    grid : GridClear = []
    for _ in range(hauteur_mat) :
        grid.append(["XXX" for _ in range(largeur_mat)])

    for i in range(hauteur_mat):
        for j in range(largeur_mat):
            content : HC = known_cells[(j,i)]
            if content == HC.EMPTY :
                grid[i][j] = "___"
            elif content == HC.CIVIL_E :
                grid[i][j] = "C-E"
            elif content == HC.CIVIL_W :
                grid[i][j] = "C-W"
            elif content == HC.CIVIL_N :
                grid[i][j] = "C-N"
            elif content == HC.CIVIL_S :
                grid[i][j] = "C-S"
            elif content == HC.GUARD_E :
                grid[i][j] = "G-E"
            elif content == HC.GUARD_W :
                grid[i][j] = "G-W"
            elif content == HC.GUARD_N :
                grid[i][j] = "G-N"
            elif content == HC.GUARD_S :
                grid[i][j] = "G-S"
            elif content == HC.PIANO_WIRE :
                grid[i][j] = "WIR"
            elif content == HC.SUIT :
                grid[i][j] = " S "
            elif content == HC.WALL:
                grid[i][j]= "WAL"
            elif content == HC.TARGET:
                grid[i][j] = "TAR"

    grid.reverse()
    return grid

############################################### PARCOURS ###############################################

def checkGuard(position : Tuple[int,int], content : HC) -> NoReturn :
    """ Checks if the content of the cell is a guard """
    global guards_field_of_view
    if (content == HC.GUARD_E):
        guards_field_of_view[position] = True
        if(position[0]<largeur_mat-1):
            guards_field_of_view[(position[0]+1, position[1])] = True
            if (position[0] < largeur_mat - 2):
                guards_field_of_view[(position[0]+2, position[1])] = True

    elif (content == HC.GUARD_W):
        guards_field_of_view[position] = True
        if (position[0] > 0 ):
            guards_field_of_view[(position[0]-1, position[1])] = True
            if (position[0] > 1):
                guards_field_of_view[(position[0]-2, position[1])] = True

    elif (content == HC.GUARD_S):
        guards_field_of_view[position] = True
        if(position[1]>0) :
            guards_field_of_view[(position[0], position[1]-1)] = True
            if (position[1] > 1):
                guards_field_of_view[(position[0], position[1]-2)] = True
    elif (content == HC.GUARD_N):
        guards_field_of_view[position] = True
        if (position[1] < hauteur_mat - 1):
            guards_field_of_view[(position[0], position[1]+1)] = True
            if (position[1] < hauteur_mat - 2):
                guards_field_of_view[(position[0], position[1]+2)] = True


def checkCivil(position : Tuple[int,int], content : HC) -> NoReturn :
    """ Checks if the content of the cell is a civil """
    if (content == HC.CIVIL_E):
        civils_field_of_view[position] = True
        if(position[0]<largeur_mat-1):
            civils_field_of_view[(position[0]+1, position[1])] = True


    elif (content == HC.CIVIL_W):
        civils_field_of_view[position] = True
        if (position[0] > 0 ):
            civils_field_of_view[(position[0]-1, position[1])] = True


    elif (content == HC.CIVIL_S):
        civils_field_of_view[position] = True
        if(position[1]>0) :
            civils_field_of_view[(position[0], position[1]-1)] = True

    elif (content == HC.CIVIL_N):
        civils_field_of_view[position] = True
        if (position[1] < hauteur_mat - 1):
            civils_field_of_view[(position[0] , position[1]+1)] = True



def getNeighbours(position : Tuple[int,int]) -> List[Tuple[int, int]]:
    """ Gets the neighbours cell of the current Hitman Position"""
    neighbours: List[Tuple[int, int]] = []
    if (position[0] > 0):
        #  and known_cells[(position[0] - 1, position[1])] == None
        neighbours.append((position[0] - 1, position[1]))
    if (position[1] < hauteur_mat - 1):
        #  and known_cells[(position[0] , position[1] +1)] == None
        neighbours.append((position[0], position[1]+1))
    if (position[1] > 0):
        #  and known_cells[(position[0], position[1] - 1)] == None
        neighbours.append((position[0], position[1] - 1))
    if (position[0] < largeur_mat - 1 ):
        #  and known_cells[(position[0] + 1, position[1])] == None
        neighbours.append((position[0]+1, position[1]))
    return neighbours



def lookAt(hr : HitmanReferee,position : Tuple[int,int],orientation : HC,neighbour : Tuple[int,int]) -> dict[str, Union[str, int, tuple[int, int], HC, list[tuple[tuple[int, int], HC]]]]:
    if(neighbour[0]==position[0]-1):
        if(orientation==HC.W):
            return hr.move()
        elif(orientation == HC.S):
            return hr.turn_clockwise()
        elif(orientation == HC.N) :
            return hr.turn_anti_clockwise()
        else :
            # à améliorer
            hr.turn_clockwise()
            return hr.turn_clockwise()

    elif(neighbour[0]==position[0]+1):
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
    else :
        if (orientation == HC.N):
            return hr.move()
        elif (orientation == HC.E):
            return hr.turn_anti_clockwise()
        elif (orientation == HC.W):
            return hr.turn_clockwise()
        else:
            # à améliorer
            hr.turn_clockwise()
            return  hr.turn_clockwise()





def explore(hr : HitmanReferee, status :  dict[str, Union[str, int, tuple[int, int], HC, list[tuple[tuple[int, int], HC]]]]) -> NoReturn :

    global known_cells
    position : Tuple[int,int] = status['position']
    path = []
    while(None in known_cells.values()):
        # Cellule de départ placée à empty
        print(status)

        if known_cells[position]==None :  known_cells[position] = HC.EMPTY
        # On récupère la vision
        for cell in status['vision']:
            known_cells[tuple(cell[0])] = HC(cell[1])
            checkGuard(tuple(cell[0]),HC(cell[1]))
            checkCivil(tuple(cell[0]),HC(cell[1]))
        # Si on connait toutes les cellules, on arrête
        if(None not in known_cells.values()) : break

        # Si on n'a pas de trajectoire à effectuer ou que le contenu de la prochaine cellule est connue
        if(len(path) ==0 or known_cells[path[len(path)-1]]!=None) :

            # On détermine les voisins
            neighbours = getNeighbours(position)

            # Calcul des cellules inconnues
            not_visited_tmp = [cell for cell in known_cells.keys() if known_cells[cell] == None]
            not_visited = []

            #Tri des cellules accessibles
            for i in range(len(not_visited_tmp)):
                if not unreachable(not_visited_tmp[i]) : not_visited.append(not_visited_tmp[i])


            # Calcul le point le plus proche, non visité
            to_visit = min(not_visited, key=lambda point: (point[0] - position[0]) ** 2 + (point[1] - position[1]) ** 2)
            print(f"To visit : {to_visit}")
            if(to_visit in neighbours):
                status = lookAt(hr,position,status['orientation'],to_visit)
            else :
                path = findPaths(position,to_visit)[0]
                # faire contrôle si on est obligé de passer par la vue d'un garde

        else :
            status = lookAt(hr,position,status["orientation"],path[path.index(position)+1])
            position = status["position"]

        pprint(generateGrid())
        print(f"Current path : {path}")
        pprint(status)
        print("****************************************************************")
    pprint(generateGrid())
    print(f"Map explored ? : {hr.send_content(known_cells)}")

def unreachable(cell : Tuple[int,int]):
    """ Determines if a cell is unreachable (no known and reachable neighbours)"""
    for neighbour in getNeighbours(cell) :
        print(neighbour)
        if known_cells[neighbour] not in [None,HC.WALL,HC.GUARD_S,HC.GUARD_E,HC.GUARD_N,HC.GUARD_W] :
            return False
    return True



def findPaths(start : Tuple[int,int], end : Tuple[int,int]):
    """Finds the best path from start to end"""
    paths = []
    explorePaths(start, end, [], paths)
    paths = sorted(paths, key=len)
    return paths

def explorePaths(current, end, path, paths): # à améliorer pour éviter de générer trop de chemins
    """Explore possible paths to find the best path"""
    global known_cells
    global guards_field_of_view

    path.append(current)    # Ajouter la cellule au chemin

    if current == end:
        paths.append(list(path))  # Ajouter une copie du chemin à la liste des chemins
    else:
        # Générer tous les mouvements possibles
        next_moves = generateNextMoves(current)
        # Explorer chaque mouvement possible
        for move in next_moves:
            # Si le chemin passe par une cellule à éviter, on ne continue pas sur cette cellule
            # or guards_field_of_view[move]==True il faut faire en sorte d'éviter ces cases
            if move!=end and (known_cells[move] in [None,HC.WALL,HC.GUARD_S,HC.GUARD_E,HC.GUARD_N,HC.GUARD_W]  or guards_field_of_view[move]==True):
                continue

            elif( paths!=[]and len(path)+1 > len(min(paths, key=len))):
                # On évite les chemins plus longs que les chemins existants
                continue
            elif move not in path:  # Vérifier si le mouvement a déjà été exploré
                explorePaths(move, end, path, paths)


    # Retirer la dernière position explorée pour revenir en arrière
    path.pop()


def generateNextMoves(current):
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





def launch_solving(hauteur : int, largeur : int, nb_guardes : int, nb_civils : int) :
    init_solving(hauteur, largeur, nb_guardes, nb_civils)




def init_solving(hauteur : int, largeur : int, nb_guardes : int, nb_civils : int):
    set_hauteur_mat(hauteur)
    set_largeur_mat(largeur)
    set_guard_count(nb_guardes)
    set_civil_count(nb_civils)
    generateUnknownCells()


############################################### CONTRAINTES ###############################################


def cell_to_variable(m: int, n: int, val: int) -> PropositionnalVariable:
    """Transforme une cellule en variable sous format DIMACS (entier)"""
    # définie de 0 à m*n -1 (m*n taille de la matrice)
    return taille_mat*val + m*largeur_mat + n + 1


def variable_to_cell(i: int) -> Tuple[int, int, int]:
    """Transforme une variable en cellule"""
    return (((i - 1) % taille_mat) // largeur_mat, (i - 1) % largeur_mat,(i - 1) // taille_mat)

def at_least_one(variables: List[PropositionnalVariable]) -> Clause:
    clause = variables[:]
    return clause

def unique(variables: List[PropositionnalVariable]) -> ClauseBase:
    #kb = [at_least_one(variables)]
    kb = []
    for v1,v2 in list(combinations(variables, 2)) :
        #kb.append([v1, v2]) #pour verif
        kb.append([-v1,-v2])
    return kb


def create_cell_constraints() -> ClauseBase:
    kb = []
    for row in range(hauteur_mat):
        for col in range(largeur_mat):
            list = []
            for val in range(1,6):
                list.append(cell_to_variable(row, col, val))
            kb += unique(list)
    return kb


def create_objects_constraints()  -> ClauseBase :
    kb = []
    for obj in (1,2) :
        list = []
        for row in range(hauteur_mat):
            for col in range(largeur_mat):
                list.append(cell_to_variable(row, col, obj))
        kb.append(at_least_one(list))
        kb += unique(list)
    return kb

def create_cible_constraints() -> ClauseBase :

    kb = []
    list = []
    for row in range(hauteur_mat):
        for col in range(largeur_mat):
            list.append(cell_to_variable(row, col, 3))
    kb.append(at_least_one(list))
    kb += unique(list)
    return kb

