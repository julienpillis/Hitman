from constraints import *
from enum import Enum
import copy

State = TypeVar("State")
Plan = List[str]
start_position: Tuple[int, int]


class Action(Enum):
    turn_clockwise = "turn_clockwise"
    turn_anticlockwise = "turn_anticlockwise"
    move = "move"
    kill_target = "kill_target"
    kill_civil = "kill_civil"
    kill_guard = "kill_guard"
    grab_suit = "grab_suit"
    grab_wire = "grab_wire"
    wear_suit = "wear_suit"


class Orientation(Enum):
    N = "N"
    W = "W"
    S = "S"
    E = "E"


fluents = {"at", "empty", "look_at", "has_wire", "has_suit", "target_killed", "is_invisible", "guard_view",
           "civil_view", "guard", "civil", "suit", "wire"}
predicats = {"target", "wall", "succView", "proximity"}

state = {"at": None,
         "empty": [],
         "look_at": None,
         "has_wire": False,
         "has_suit": False,
         "target_killed": False,
         "is_invisible": False,
         "guard_view": {},
         "civil_view": {},
         "guard": {},
         "civil": {},
         "suit": None,
         "wire": None,
         "target": None,
         "wall": [],
         "succView": {Orientation.N: Orientation.E, Orientation.E: Orientation.S, Orientation.S: Orientation.W,
                      Orientation.W: Orientation.N},
         "proximity": {}
         }


def get_key(val, dict):
    """Retourne la clé d'une valeur dans un dictionnaire"""
    for key, value in dict.items():
        if val == value:
            return key

    return "key doesn't exist"


def initial_state(map: Dict[Tuple[int, int], HC], start_pos: Tuple[int, int], looking_at: HC, hauteur: int,
                  largeur: int) -> State:
    """Initialise l'état initial, en début de phase 2 """
    global state, hauteur_mat, largeur_mat, start_position
    hauteur_mat = hauteur
    largeur_mat = largeur
    state['at'] = start_pos
    start_position = start_pos
    if (looking_at == HC.N):
        state['look_at'] = Orientation.N
    elif (looking_at == HC.S):
        state['look_at'] = Orientation.S
    elif (looking_at == HC.E):
        state['look_at'] = Orientation.E
    else:
        state['look_at'] = Orientation.W
    for cell in map:
        if (map[cell] in [HC.EMPTY, HC.SUIT, HC.TARGET, HC.PIANO_WIRE]):
            state['empty'].append(cell)
        if map[cell] == HC.WALL:
            state['wall'].append(cell)
        elif map[cell] == HC.SUIT:
            state['suit'] = cell
        elif (map[cell] == HC.TARGET):
            state['target'] = cell
        elif (map[cell] == HC.PIANO_WIRE):
            state['wire'] = cell
        elif map[cell] == HC.GUARD_N:
            state['guard'][cell] = Orientation.N
        elif (map[cell] == HC.GUARD_S):
            state['guard'][cell] = Orientation.S
        elif (map[cell] == HC.GUARD_E):
            state['guard'][cell] = Orientation.E
        elif map[cell] == HC.GUARD_W:
            state['guard'][cell] = Orientation.W
        elif map[cell] == HC.CIVIL_N:
            state['civil'][cell] = Orientation.N
        elif map[cell] == HC.CIVIL_S:
            state['civil'][cell] = Orientation.S
        elif (map[cell] == HC.CIVIL_E):
            state['civil'][cell] = Orientation.E
        elif (map[cell] == HC.CIVIL_W):
            state['civil'][cell] = Orientation.W

        # Détermination des cellules voisines de la cellule
        for orientation in Orientation:
            ngh = find_neighbour(cell, orientation)
            if ngh is not None:
                state['proximity'][(cell, orientation)] = ngh

    # On étudie les zones visibles par les gardes et les civils
    define_view()

    return state


def find_neighbour(cell: Tuple[int, int], orientation: Orientation) -> Optional[Tuple[int, int]]:
    """Détermine la cellule voisine en fonction de l'orientation (ex : Nord -> cellule au dessus)"""
    if (orientation == Orientation.N):
        if (cell[1] == hauteur_mat - 1):
            return None
        else:
            return (cell[0], cell[1] + 1)

    elif (orientation == Orientation.S):
        if (cell[1] == 0):
            return None
        else:
            return (cell[0], cell[1] - 1)

    elif (orientation == Orientation.E):
        if (cell[0] == largeur_mat - 1):
            return None
        else:
            return (cell[0] + 1, cell[1])
    else:
        if (cell[0] == 0):
            return None
        else:
            return (cell[0] - 1, cell[1])


def define_view() -> NoReturn:
    """Détermine les zones où les gardes et civils peuvent voir"""
    global state
    for cell in state['guard']:
        orientation = state['guard'][cell]
        zone = []
        if (orientation == Orientation.N):
            row_max = min([cell[1] + 2, hauteur_mat - 1])
            for row in range(cell[1], row_max + 1):
                zone.append((cell[0], row))

        elif (orientation == Orientation.S):
            row_min = max([cell[1] - 2, 0])
            for row in range(row_min, cell[1] + 1):
                zone.append((cell[0], row))

        elif (orientation == Orientation.E):
            col_max = min([cell[0] + 2, largeur_mat - 1])
            for col in range(cell[0], col_max + 1):
                zone.append((col, cell[1]))
        else:
            col_min = max([cell[0] - 2, 0])
            for col in range(col_min, cell[0] + 1):
                zone.append((col, cell[1]))

        state['guard_view'][cell] = zone

    for cell in state['civil']:
        zone = []
        orientation = state['civil'][cell]
        if (orientation == Orientation.N):
            row_max = min([cell[1] + 1, hauteur_mat - 1])
            for row in range(cell[1], row_max + 1):
                zone.append((cell[0], row))


        elif (orientation == Orientation.S):
            row_min = max([cell[1] - 1, 0])
            for row in range(row_min, cell[1] + 1):
                zone.append((cell[0], row))

        elif (orientation == Orientation.E):
            col_max = min([cell[0] + 1, largeur_mat - 1])
            for col in range(cell[0], col_max + 1):
                zone.append((col, cell[1]))
        else:
            col_min = max([cell[0] - 1, 0])
            for col in range(col_min, cell[0] + 1):
                zone.append((col, cell[1]))

        state['civil_view'][cell] = zone


#####################################################################################################
########################### IMPLEMENTATION DE LA MODELISATION STRIPS ################################
#####################################################################################################


def turn_clockwise(state: State) -> Optional[Tuple[State, int]]:
    """Action STRIPS : tourner à 90 °"""
    new_state: State = copy.deepcopy(state)
    orientation = state["look_at"]
    if (orientation != None):
        new_orientation = Orientation(state['succView'][orientation])
        new_state['look_at'] = new_orientation
        return (new_state, 1)
    return None


def turn_anticlockwise(state: State) -> Optional[Tuple[State, int]]:
    """Action STRIPS : tourner à -90° """
    new_state: State = copy.deepcopy(state)
    orientation = state["look_at"]
    if (orientation != None):
        new_orientation = Orientation(get_key(orientation, state['succView']))
        new_state['look_at'] = new_orientation
        return (new_state, 1)
    return None


def move(state: State) -> Optional[Tuple[State, int]]:
    """Action STRIPS : avancer (tout droit)"""
    new_state: State = copy.deepcopy(state)
    pos = state["at"]
    ori = state["look_at"]
    cost = 1
    if (pos != None):
        if ((pos, ori) in state['proximity'].keys()):
            new_pos = state['proximity'][(pos, ori)]
            if (new_pos in state['empty']):
                new_state['at'] = new_pos
                for zone in new_state['guard_view'].values():
                    cost += zone.count(pos) * 5
                return (new_state, cost)
    return None


def kill_target(state: State) -> Optional[Tuple[State, int]]:
    """Action STRIPS :tuer la cible"""
    new_state: State = copy.deepcopy(state)
    pos = state["at"]
    if (pos != None and state['has_wire'] and pos == state['target']):
        new_state['target_killed'] = True
        cost = 1
        if (state['is_invisible']):
            return (new_state, 0)
        else:
            # Malus si dans le champ de vision de quelqu'un, et sans costume
            for zone in state['guard_view'].values():
                cost += zone.count(pos) * 100
            for zone in state['civil_view'].values():
                cost += zone.count(pos) * 100
            return (new_state, cost)
    return None


def kill_guard(state: State) -> Optional[Tuple[State, int]]:
    """Action STRIPS : tuer un garde"""
    new_state: State = copy.deepcopy(state)
    pos = state["at"]
    ori = state["look_at"]
    if (pos != None and ori != None and state['has_wire']):
        if ((pos, ori) in state['proximity'].keys() and (state['proximity'][(pos, ori)] in state['guard'].keys())):
            to_kill = state['proximity'][(pos, ori)]
            if (to_kill in state['guard'].keys()):
                if (pos not in state['guard_view'][to_kill]):
                    cost = 21
                    new_state['guard'].pop(to_kill)
                    new_state['guard_view'].pop(to_kill)
                    new_state['empty'].append(to_kill)
                    if (state['is_invisible']):
                        return (new_state, cost)
                    for zone in new_state['guard_view'].values():
                        cost += zone.count(pos) * 100
                    for zone in new_state['civil_view'].values():
                        cost += zone.count(pos) * 100
                    return (new_state, cost)
    return None


def kill_civil(state: State) -> Optional[Tuple[State, int]]:
    """Action STRIPS : tuer un civil"""
    new_state: State = copy.deepcopy(state)
    pos = state["at"]
    ori = state["look_at"]
    if (pos != None and ori != None and state['has_wire']):
        if ((pos, ori) in state['proximity'].keys() and (state['proximity'][(pos, ori)] in state['civil'].keys())):
            to_kill = state['proximity'][(pos, ori)]

            if (to_kill in state['civil'].keys()):
                if (pos not in state['civil_view'][to_kill]):
                    cost = 21
                    new_state['civil'].pop(to_kill)
                    new_state['civil_view'].pop(to_kill)
                    new_state['empty'].append(to_kill)
                    if (state['is_invisible']):
                        return (new_state, cost)
                    for zone in new_state['guard_view'].values():
                        cost += zone.count(pos) * 100
                    for zone in new_state['civil_view'].values():
                        cost += zone.count(pos) * 100
                    return (new_state, cost)
    return None


def grab_suit(state: State) -> Optional[Tuple[State, int]]:
    """Action STRIPS : attraper le déguisement"""
    new_state: State = copy.deepcopy(state)
    pos = state["at"]
    if (pos != None and state['suit'] == pos):
        new_state['has_suit'] = True
        new_state['suit'] = None
        return (new_state, 1)
    return None


def wear_suit(state: State) -> Optional[Tuple[State, int]]:
    """Action STRIPS : porter le déguisement"""
    new_state: State = copy.deepcopy(state)
    pos = state['at']
    if (state['has_suit'] and not state['is_invisible']):
        new_state['is_invisible'] = True
        cost = 1
        for zone in state['guard_view'].values():
            cost += zone.count(pos) * 100
        for zone in state['civil_view'].values():
            cost += zone.count(pos) * 100
        return (new_state, cost)
    return None


def grab_wire(state: State) -> Optional[Tuple[State, int]]:
    """Action STRIPS : attraper la corde de piano"""
    new_state: State = copy.deepcopy(state)
    pos = state["at"]
    if (pos != None and state['wire'] == pos):
        new_state['has_wire'] = True
        new_state['wire'] = None
        return (new_state, 1)
    return None


#####################################################################################################
########################### ALGORITHME D'OPTIMISATION DE STRATEGIE A* ###############################
#####################################################################################################


class Node:
    """ Définition d'un nœud. Utilisé pour l'algorithme A*"""
    def __init__(self, state: State, cost: int, action: Action = None, parent=None, ):
        self.state = state # Etat du noeud
        self.action = action  # Action nécessaire pour l'obtention du mvt
        self.cost = cost  # Coût actuel depuis le nœud de départ
        self.parent = parent  # Parent du nœud dans le chemin


def astar(start: State, goal: str) -> Optional:
    """Implémentation de l'algorithme de recherche informée A*"""
    to_check = []
    closed_set = []

    # On introduit l'état initial de coût 0, et l'action Nulle
    start_node = Node(start, 0)
    to_check.append(start_node)
    while to_check:
        current_node = to_check.pop(0)
        # Cas de l'objectif atteint
        # recherche du chemin optimal vers la corde
        if goal == "wire" and current_node.state['has_wire']:
            path = []
            node = current_node
            expected_cost = 0
            while node.parent is not None:
                path.append(node.action)
                expected_cost += node.cost
                node = node.parent
            path.reverse()

            return path, expected_cost, current_node.state
        # recherche du chemin optimal vers la cible
        elif goal == "target" and current_node.state['target_killed']:
            path = []
            node = current_node
            expected_cost = 0
            while node.parent is not None:
                path.append(node.action)
                expected_cost += node.cost
                node = node.parent
            path.reverse()

            return path, expected_cost, current_node.state

        # recherche du chemin optimal vers la position de départ
        elif goal == "leave" and current_node.state['at'] == start_position:
            path = []
            node = current_node
            expected_cost = 0
            while node.parent is not None:
                path.append(node.action)
                expected_cost += node.cost
                node = node.parent
            path.reverse()

            return path, expected_cost, current_node.state
        # Cas de l'objectif non atteint

        # si l'état n'a jamais été visité, on l'ajoute à la liste des noeuds visités
        if (current_node.state not in closed_set):
            closed_set.append(current_node.state)

        # Calcul des actions possibles par l'état actuel
        actions = next_actions(current_node.state)

        for action in actions:
            # on passe à la prochaine itération si l'état a déjà été visité
            if (action[0][0] in closed_set):
                continue

            after_action_cost = action[0][1] + current_node.cost
            after_action_node = Node(action[0][0], after_action_cost, action[1], current_node)
            
              """
                # Estimation heuristique (distance de Manhattan)
            heuristic_cost = manhattan_distance(after_action_node.state, goal)

            after_action_node.cost += heuristic_cost
            """

            if after_action_node in to_check:
                existing_node_index = to_check.index(after_action_node)
                existing_node = to_check[existing_node_index]

                if after_action_node.cost < existing_node.cost:
                    to_check[existing_node_index] = after_action_node

            else:
                to_check.append(after_action_node)
                """
                to_check.sort(key=lambda node: node.cost)  # Tri des nœuds en fonction du coût total
                """
    return None


def next_actions(state_t : State) -> list[Union[tuple[tuple[State, int], Action], tuple[State, Action]]]:
    """Détermination des actions possibles à l'état state """
    to_test = []

    new_state_w_cost = turn_clockwise(state_t)
    if (new_state_w_cost != None):
        to_test.append((new_state_w_cost, Action.turn_clockwise))

    new_state_w_cost = turn_anticlockwise(state_t)
    if (new_state_w_cost != None):
        to_test.append((new_state_w_cost, Action.turn_anticlockwise))

    new_state_w_cost = move(state_t)
    if (new_state_w_cost != None):
        to_test.append((new_state_w_cost, Action.move))

    if (not state['has_suit']):
        new_state_w_cost = grab_suit(state_t)
        if (new_state_w_cost != None):
            to_test.append((new_state_w_cost, Action.grab_suit))

    if (not state['has_wire']):
        new_state_w_cost = grab_wire(state_t)
        if (new_state_w_cost != None):
            to_test.append((new_state_w_cost, Action.grab_wire))

    if (not state['is_invisible']):
        new_state_w_cost = wear_suit(state_t)
        if (new_state_w_cost != None):
            to_test.append((new_state_w_cost, Action.wear_suit))

    new_state_w_cost = kill_target(state_t)
    if (new_state_w_cost != None):
        to_test.append((new_state_w_cost, Action.kill_target))

    new_state_w_cost = kill_guard(state_t)
    if (new_state_w_cost != None):
        to_test.append((new_state_w_cost, Action.kill_guard))

    new_state_w_cost = kill_civil(state_t)
    if (new_state_w_cost != None):
        to_test.append((new_state_w_cost, Action.kill_civil))

    return to_test



#####################################################################################################
############################## FONCTION DE DEMARRAGE DE LA PHASE 2 ##################################
#####################################################################################################


def launch_killing(state_t: State, hr: HitmanReferee) -> NoReturn:
    """ Lancement de la phase 2, objectif : tuer la cible et fuir """

    # Premièrement, il faut récupérer la corde de piano
    print("Getting piano wire...")
    path_wire, cost_wire, wired_state = astar(state_t, "wire")

    # Puis, il faut tuer la corde de piano
    print("Going to target...")
    path_target, cost_target, tk_state = astar(wired_state, "target")

    # Enfin, il faut fuir
    print("Leaving the area...")
    path_leave, cost_leave, tk_leave = astar(tk_state, "leave")

    print(f"Path : {path_wire + path_target + path_leave}")
    print(f"Estimated cost : {cost_target + cost_wire + cost_leave}")

    # Execution des actions de déplacement
    for action in path_wire + path_target + path_leave:
        if (action == Action.turn_clockwise):
            status = hr.turn_clockwise()
            print(status)
        elif (action == Action.turn_anticlockwise):
            status = hr.turn_anti_clockwise()
            print(status)
        elif action == Action.move:
            status = hr.move()
            print(status)
        elif action == Action.kill_target:
            status = hr.kill_target()
            print(status)
        elif (action == Action.grab_wire):
            status = hr.take_weapon()
            print(status)
        elif (action == Action.kill_civil):
            status = hr.neutralize_civil()
            print(status)
        elif (action == Action.kill_guard):
            status = hr.neutralize_guard()
            print(status)
        print(action)

        
  ##################################################
"""
def manhattan_distance(state: State, goal: str) -> int:
    """Calcule la distance de Manhattan entre l'état actuel et l'état objectif."""
    if goal == "wire":
        goal_position = state['wire_position']
    elif goal == "target":
        goal_position = state['target_position']
    elif goal == "leave":
        goal_position = start_position  # Remplacez start_position par la position de départ réelle
    else:
        raise ValueError("Objectif invalide")

    current_position = state['at']
    distance = abs(current_position[0] - goal_position[0]) + abs(current_position[1] - goal_position[1])
    return distance

"""

"""

def heuristic_distance(state: State, goal: str) -> int:
    if goal == 'target':
        return manhattan_distance(state['at'], state['target'])
    # Ajoutez d'autres cas si nécessaire
    return 0


def heuristic_guards(state: State) -> int:
    num_guards = 0
    for guard_view in state['guard_view'].values():
        if state['at'] in guard_view:
            num_guards += 1
    return num_guards


def heuristic_invisibility(state: State) -> int:
    if state['is_invisible']:
        return 0  # Le joueur est invisible, aucun coût supplémentaire
    return 1  # Le joueur n'est pas invisible, coût supplémentaire de 1


def heuristic_global(state: State, goal: str) -> int:
    distance = manhattan_distance(state['at'], state['target'])
    guards = heuristic_guards(state)
    civils = heuristic_civils(state)
    invisibility = heuristic_invisibility(state)

    # Vous pouvez ajuster les coefficients selon votre besoin
    return distance + 2 * guards + 2 * civils +
    """
