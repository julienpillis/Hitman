from hitman.hitman import HC, HitmanReferee, complete_map_example6, world_example, complete_map_example2
from pprint import pprint
from constraints import *
from phase2 import *
from pprint import pprint


def phase1_run(hr):
    status = hr.start_phase1()
    init_exploration(status['m'], status['n'], status['guard_count'], status['civil_count'])
    explore(hr, status)

def phase2_run(hr):
    status = hr.start_phase2()
    state_t = initial_state(complete_map_example6,status['position'],status['orientation'],status['m'],status['n'])
    launch_killing(state_t,hr)

def main():


    hr = HitmanReferee()
    status = hr.start_phase2()
    pprint(status)
    phase2_run(hr)
    _, score, history = hr.end_phase2()
    pprint(score)
    pprint(history)

    """
    
    hr = HitmanReferee()
    status = hr.start_phase1()
    pprint(status)
    phase1_run(hr)
    _, score, history, true_map = hr.end_phase1()
    pprint(score)
    pprint(true_map)
    pprint(history)

    """





if __name__ == "__main__":
    main()




"""
def main():
    print("***********************INIT*****************************")
    hr = HitmanReferee()
    status = hr.start_phase1()
    pprint(status)
    launch_solving(status['m'],status['n'],status['guard_count'],status['civil_count'])
    print("********************************************************")
    #print(cell_to_variable((0,1), HC.GUARD_N))
    #print(variable_to_cell(92))
    #print(variable_to_cell(cell_to_variable((0, 6), HC.EMPTY)))
    #dimacs = clauses_to_dimacs(generate_constraints()+constraints_listener((0,0),0) + [[-cell_to_variable((6,4), HC.GUARD_N)]], 7,header=True)
    #write_dimacs_file(dimacs, "hitman.cnf")
    #print(exec_gophersat("hitman.cnf")[0])
    #rebuild(exec_gophersat("hitman.cnf")[1])
    explore(hr,status)

"""

