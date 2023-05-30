from itertools import combinations
from hitman.hitman import HC, HitmanReferee, complete_map_example
from pprint import pprint
from typing import *
from math import *
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
guards_field_of_view : Dict[Tuple[int,int],HC] = {} # Cellules vues par les gardes | None : Inconnue | True : vue par un garde | False : non vue par un garde
civils_field_of_view : Dict[Tuple[int,int],HC] = {} # Cellules vues par les civils | None : Inconnue | True : vue par un civil | False : non vue par un civil
## Plateau






############################################### SETTERS ###############################################
def set_hauteur_mat(h : int) -> NoReturn :
    """ Set the value of hauteur_mat """
    global hauteur_mat
    hauteur_mat = h

def set_largeur_mat(l : int) -> NoReturn:
    """ Set the value of largeur_mat """
    global largeur_mat
    largeur_mat = l

def set_civil_count(nb : int) -> NoReturn:
    """ Set the value of largeur_mat """
    global civil_count
    civil_count = nb

def set_guard_count(nb : int) -> NoReturn:
    """ Set the value of largeur_mat """
    global guard_count
    guard_count = nb

def generateUnknownCells() -> NoReturn :
    """Generate grid of cells """
    global known_cells
    global guards_field_of_view
    global civils_field_of_view
    for i in range(hauteur_mat):

        for j in range(largeur_mat):
            known_cells[(i,j)] = None
            guards_field_of_view[(i,j)] = None
            civils_field_of_view[(i,j)] = None

############################################### AFFICHAGE ###############################################


def launch_solving(hauteur : int, largeur : int, nb_guardes : int, nb_civils : int) :
    set_hauteur_mat(hauteur)
    set_largeur_mat(largeur)
    set_guard_count(nb_guardes)
    set_civil_count(nb_civils)
    generateUnknownCells()
    print(f"{hauteur_mat},{largeur_mat},{guard_count},{civil_count}")
    print(f"{known_cells}")
    print(f"{guards_field_of_view}")




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

