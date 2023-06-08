from typing import *
from constraints import *
import heapq
from enum import Enum
import copy

State = TypeVar("State")
Plan = List[str]
str_to_action : Dict[str,Callable[[State],Optional[State]]]

complete_map_example = {
    (0, 5): HC.EMPTY,
    (1, 5): HC.EMPTY,
    (2, 5): HC.EMPTY,
    (3, 5): HC.SUIT,
    (4, 5): HC.GUARD_S,
    (5, 5): HC.WALL,
    (6, 5): HC.WALL,
    (0, 4): HC.EMPTY,
    (1, 4): HC.WALL,
    (2, 4): HC.EMPTY,
    (3, 4): HC.EMPTY,
    (4, 4): HC.EMPTY,
    (5, 4): HC.EMPTY,
    (6, 4): HC.EMPTY,
    (0, 3): HC.TARGET,
    (1, 3): HC.WALL,
    (2, 3): HC.EMPTY,
    (3, 3): HC.EMPTY,
    (4, 3): HC.EMPTY,
    (5, 3): HC.CIVIL_N,
    (6, 3): HC.EMPTY,
    (0, 2): HC.WALL,
    (1, 2): HC.WALL,
    (2, 2): HC.EMPTY,
    (3, 2): HC.GUARD_E,
    (4, 2): HC.EMPTY,
    (5, 2): HC.CIVIL_E,
    (6, 2): HC.CIVIL_W,
    (0, 1): HC.EMPTY,
    (1, 1): HC.EMPTY,
    (2, 1): HC.EMPTY,
    (3, 1): HC.EMPTY,
    (4, 1): HC.EMPTY,
    (5, 1): HC.EMPTY,
    (6, 1): HC.EMPTY,
    (0, 0): HC.EMPTY,
    (1, 0): HC.EMPTY,
    (2, 0): HC.WALL,
    (3, 0): HC.WALL,
    (4, 0): HC.EMPTY,
    (5, 0): HC.PIANO_WIRE,
    (6, 0): HC.EMPTY,
}

class Action(Enum) :
    turn_clockwise = "turn_clockwise"
    turn_anticlockwise = "turn_anticlockwise"
    move = "move"
    kill_target = "kill_target"
    kill_civil = "kill_civil"
    kill_guard = "kill_guard"
    grab_suit = "grab_suit"
    grab_wire = "grab_wire"
    wear_suit = "wear_suit"

class Orientation(Enum) :
    N = "N"
    W = "W"
    S = "S"
    E = "E"


fluents = {"at","empty","look_at","has_wire","has_suit","target_killed","is_invisible","guard_view","civil_view","guard","civil","suit","wire"}
predicats = {"target","wall","succView","proximity"}

state = {"at":None,
         "empty":[],
         "look_at":None,
         "has_wire":False,
         "has_suit":False,
         "target_killed":False,
         "is_invisible":False,
         "guard_view" :{},
         "civil_view":{},
         "guard": {},
         "civil":{},
         "suit":None,
         "wire":None,
         "target":None,
         "wall":[],
         "succView":{Orientation.N:Orientation.E,Orientation.E:Orientation.S,Orientation.S:Orientation.W,Orientation.W:Orientation.N},
         "proximity":{}
         }

def initial_state(map : Dict[Tuple[int, int], HC],start_pos : Tuple[int,int],looking_at : HC, hauteur : int, largeur : int) -> NoReturn:
    "Initial state"
    global state,hauteur_mat,largeur_mat
    hauteur_mat = hauteur
    largeur_mat = largeur
    state['at'] = start_pos
    if(looking_at==HC.N):state['look_at'] = Orientation.N
    elif (looking_at == HC.S): state['look_at'] = Orientation.S
    elif (looking_at == HC.E): state['look_at'] = Orientation.E
    else : state['look_at'] = Orientation.W
    for cell in map :
        if(map[cell] in [HC.EMPTY,HC.SUIT,HC.TARGET,HC.PIANO_WIRE]):
            state['empty'].append(cell)
        if(map[cell]==HC.WALL) :
            state['wall'].append(cell)
        elif (map[cell] == HC.SUIT):
            state['suit'] = cell
        elif (map[cell] == HC.TARGET):
            state['target'] = cell
        elif (map[cell] == HC.PIANO_WIRE):
            state['wire'] = cell
        elif (map[cell] == HC.GUARD_N):
            state['guard'][cell] = Orientation.N
        elif (map[cell] == HC.GUARD_S):
            state['guard'][cell] = Orientation.S
        elif (map[cell] == HC.GUARD_E):
            state['guard'][cell] = Orientation.E
        elif (map[cell] == HC.GUARD_W):
            state['guard'][cell] = Orientation.W
        elif (map[cell] == HC.CIVIL_N):
            state['civil'][cell] = Orientation.N
        elif (map[cell] == HC.CIVIL_S):
            state['civil'][cell] = Orientation.S
        elif (map[cell] == HC.CIVIL_E):
            state['civil'][cell] = Orientation.E
        elif (map[cell] == HC.CIVIL_W):
            state['civil'][cell] = Orientation.W

        for orientation in Orientation:
            # trouve le voisin de la cellule en fontion de la direction
            ngh = find_neighbour(cell,orientation)
            if ngh != None :
                state['proximity'][(cell,orientation)] = ngh

    define_view()
    pprint(state)
    s = turn_clockwise(state)[0]
    print(s['look_at'])
    if(move(s)!=None):
        print(move(s)[0]['at'])
        s = move(s)[0]
    pprint(s)
    if (move(s) != None):
        print(move(s)[0]['at'])
        s = move(s)[0]

    return state

def find_neighbour(cell : Tuple[int,int], orientation : Orientation):
    """Find the neighbour cell, with orientation"""
    if(orientation == Orientation.N):
        if(cell[1]==hauteur_mat-1) : return None
        else :
            return (cell[0],cell[1]+1)

    elif (orientation == Orientation.S):
        if (cell[1] == 0):
            return None
        else:
            return (cell[0], cell[1] - 1)

    elif (orientation == Orientation.E):
        if (cell[0] == largeur_mat-1):
            return None
        else:
            return (cell[0]+1, cell[1])
    else :
        if (cell[0] == 0):
            return None
        else:
            return (cell[0]-1, cell[1])

def define_view():
    global state
    for cell in state['guard'] :
        orientation = state['guard'][cell]
        zone = []
        if(orientation==Orientation.N) :
            row_max = min([cell[1] + 2, hauteur_mat - 1])
            for row in range(cell[1],row_max+1):
                zone.append((cell[0],row))

        elif (orientation == Orientation.S):
            row_min = max([cell[1] - 2, 0])
            for row in range(row_min,cell[1]+1):
                zone.append((cell[0], row))

        elif (orientation == Orientation.E):
            col_max = min([cell[0] + 2, largeur_mat- 1])
            for col in range(cell[0], col_max + 1):
                zone.append((col, cell[1]))
        else:
            col_min = max([cell[0] - 2, 0])
            for col in range(col_min,cell[0]+1):
                zone.append((col, cell[1]))

        state['guard_view'][cell] = zone

    for cell in state['civil']:
        zone = []
        print(cell[0],cell[1])
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


def turn_clockwise(state : State) -> Tuple[State,int]:
    new_state: State = copy.deepcopy(state)
    orientation = state["look_at"]
    if(orientation!=None) :
        new_orientation = Orientation(state['succView'][orientation])
        new_state['look_at'] = new_orientation
        return (new_state,1)
    return None

def turn_anticlockwise(state : State) -> State:
    new_state: State = copy.deepcopy(state)
    orientation = state["look_at"]
    if (orientation != None):
        new_orientation = Orientation(get_key(orientation,state['succView']))
        new_state['look_at'] = new_orientation
        return (new_state, 1)
    return None

def move(state : State) -> State:
    new_state: State = copy.deepcopy(state)
    pos = state["at"]
    ori = state["look_at"]
    if(pos != None):
        if((pos,ori) in state['proximity'].keys()):
            new_pos = state['proximity'][(pos,ori)]
            if(new_pos in state['empty']):
                new_state['at'] = new_pos
                return (new_state,1)
    return None

def kill_target(state : State) -> State:
    new_state: State = copy.deepcopy(state)
    pos = state["at"]
    if(pos!=None and state['has_wire'] and pos==state['target']):
        new_state['target_killed']=True
        cost = 0
        if(state['is_invisible']):
            return (new_state,0)
        else:
            # Malus si dans le champ de vision de quelqu'un, et sans costume
            for zone in state['guard_view'].values():
                cost+=zone.count(pos)*100
            for zone in state['civil_view'].values():
                cost += zone.count(pos) * 100
            return(new_state,cost)
    return None

def kill_guard(state : State) -> State:
    new_state: State = copy.deepcopy(state)
    pos = state["at"]
    ori = state["look_at"]
    if (pos != None and ori !=None and state['has_wire']):
        if ((pos, ori) in state['proximity'].keys() and (state['proximity'][(pos, ori)] in state['guard'].keys()) ):
            to_kill = state['proximity'][(pos, ori)]
            if(to_kill in state['guard'].keys()):
                if(state['guard'][to_kill]!=ori):
                    cost = 1
                    new_state['guard'].pop(to_kill)
                    new_state['guard_view'].pop(to_kill)
                    new_state['empty'].append(to_kill)
                    if (state['is_invisible']):
                        return (new_state, 20)
                    for zone in state['guard_view'].values():
                        cost += zone.count(pos) * 100
                    for zone in state['civil_view'].values():
                        cost += zone.count(pos) * 100
                    return (new_state, cost + 20)
    return None

def kill_civil(state : State) -> State:
    new_state: State = copy.deepcopy(state)
    pos = state["at"]
    ori = state["look_at"]
    if (pos != None and ori !=None and state['has_wire']):
        if ((pos, ori) in state['proximity'].keys() and (state['proximity'][(pos, ori)] in state['civil'].keys()) ):
            to_kill = state['proximity'][(pos, ori)]

            if(to_kill in state['civil'].keys()):
                if(state['civil'][to_kill]!=ori):
                    cost = 1
                    new_state['civil'].pop(to_kill)
                    new_state['civil_view'].pop(to_kill)
                    new_state['empty'].append(to_kill)
                    if (state['is_invisible']):
                        return (new_state, 20)
                    for zone in state['guard_view'].values():
                        cost += zone.count(pos) * 100
                    for zone in state['civil_view'].values():
                        cost += zone.count(pos) * 100
                    return(new_state,cost + 20)
    return None

def grab_suit(state : State) -> State:
    new_state: State = copy.deepcopy(state)
    pos = state["at"]
    if(pos!=None and state['suit']==pos):
        new_state['has_suit'] = True
        new_state['suit'] = None
        return(new_state,1)
    return None

def wear_suit(state : State) -> State:
    new_state: State = copy.deepcopy(state)
    pos = state['at']
    if(state['has_suit'] and not state['is_invisible']):
        new_state['is_invisible'] = True
        cost = 1
        for zone in state['guard_view'].values():
            cost += zone.count(pos) * 100
        for zone in state['civil_view'].values():
            cost += zone.count(pos) * 100
        return(new_state,cost)
    return None

def grab_wire(state : State) -> State:
    new_state: State = copy.deepcopy(state)
    pos = state["at"]
    if (pos != None and state['wire'] == pos):
        new_state['has_wire'] = True
        new_state['wire'] = None
        return (new_state, 1)
    return None





def is_final(state : State) -> bool:
    return state["target_killed"]

# Fonctions utiles
def get_key(val,dict):
    for key, value in dict.items():
        if val == value:
            return key

    return "key doesn't exist"

class Node:
    def __init__(self,state : State, cost : int, action : Action = None,parent=None, ):
        self.state = state
        self.action = action  # Action nécessaire pour l'obtention du mvt
        self.cost = cost  # Coût actuel depuis le nœud de départ
        self.parent = parent  # Parent du nœud dans le chemin

def astar(start : State):
    to_check = []
    closed_set = []


    # On introduit l'état initial de coût 0, et l'action Nulle
    start_node = Node(start,0)
    to_check.append(start_node)
    while to_check :
        current_node = to_check.pop(0)
        # Cas de l'objectif atteint
        if is_final(current_node.state) :
            path = []
            node = current_node
            expected_cost = 0
            while node.parent is not None :
                path.append(node.action)
                expected_cost+=node.cost
                node = node.parent
                print(node.state['guard'])
            path.reverse()
            return path,expected_cost

        # Cas de l'objectif non atteint

        #si l'état n'a jamais été visité, on l'ajoute à la liste des noeuds visités
        if(current_node.state not in closed_set):
            closed_set.append(current_node.state)

        # Calcul des actions possibles par l'état actuel
        actions = next_actions(current_node.state)

        for action in actions :
            # on passe à la prochaine itération si l'état a déjà été visité
            if(action[0][0] in closed_set):
                continue

            after_action_cost = action[0][1] + current_node.cost
            after_action_node = Node(action[0][0],after_action_cost,action[1],current_node)


            if after_action_node in to_check:
                existing_node_index = to_check.index(after_action_node)
                existing_node = to_check[existing_node_index]

                if after_action_node.cost < existing_node.cost:
                    to_check[existing_node_index] = after_action_node

            else:
                to_check.append(after_action_node)




def next_actions(state):
    to_test = []

    new_state_w_cost = turn_clockwise(state)
    if(new_state_w_cost!=None):
        to_test.append((new_state_w_cost,Action.turn_clockwise))

    new_state_w_cost = turn_anticlockwise(state)
    if (new_state_w_cost != None):
        to_test.append((new_state_w_cost, Action.turn_anticlockwise))

    new_state_w_cost = move(state)
    if (new_state_w_cost != None):
        to_test.append((new_state_w_cost, Action.move))

    new_state_w_cost = kill_target(state)
    if (new_state_w_cost != None):
        to_test.append((new_state_w_cost, Action.kill_target))

    new_state_w_cost = kill_guard(state)
    if (new_state_w_cost != None):
        to_test.append((new_state_w_cost, Action.kill_guard))

    new_state_w_cost = kill_civil(state)
    if (new_state_w_cost != None):
        to_test.append((new_state_w_cost, Action.kill_civil))

    new_state_w_cost = grab_suit(state)
    if (new_state_w_cost != None):
        to_test.append((new_state_w_cost, Action.grab_suit))

    new_state_w_cost = grab_wire(state)
    if (new_state_w_cost != None):
        to_test.append((new_state_w_cost, Action.grab_wire))

    new_state_w_cost = wear_suit(state)
    if (new_state_w_cost != None):
        to_test.append((new_state_w_cost, Action.wear_suit))
    return to_test