from hitman.hitman import HC, HitmanReferee, complete_map_example, world_example
from pprint import pprint
from constraints import *






def main():
    print("***********************INIT*****************************")
    hr = HitmanReferee()
    status = hr.start_phase1()
    pprint(status)
    launch_solving(status['m'],status['n'],status['guard_count'],status['civil_count'])
    print("********************************************************")
    #print(cell_to_variable((6,0), HC.EMPTY))
    #print(variable_to_cell(cell_to_variable((0,1), HC.WALL)))
    #print(variable_to_cell(cell_to_variable((0, 6), HC.EMPTY)))
    explore(hr,status)

"""
    hr = HitmanReferee()
    status = hr.start_phase1()
    pprint(status)
    launch_solving(status['m'], status['n'], status['guard_count'], status['civil_count'])

    #print(cell_to_variable((3,4),HC.EMPTY))
    #print(variable_to_cell(cell_to_variable((3,4),HC.EMPTY)))

    kb = generate_constraints()
    #print(kb)
    #print(cell_to_variable((6,5),HC.PIANO_WIRE))
    dimacs = clauses_to_dimacs(kb,7)
    #print(dimacs)
    write_dimacs_file(dimacs,"hitman.cnf")
    #print(dimacs)
    #print(exec_gophersat("hitman.cnf"))
    rebuild(exec_gophersat("hitman.cnf")[1])

    #print(variable_to_cell(1092))
  
    status = hr.turn_clockwise()
    pprint(status)
    explore(hr, status)
    pprint(status)
    status = hr.turn_clockwise()
    explore(hr, status)
    pprint(status)
    status = hr.turn_clockwise()
    explore(hr, status)
    pprint(status)
    status = hr.turn_clockwise()
    explore(hr, status)
    pprint(status)
    status = hr.move()
    explore(hr, status)
    pprint(status)
    status = hr.move()
    explore(hr, status)
    pprint(status)
    status = hr.turn_clockwise()
    explore(hr, status)

    pprint(status)
    status = hr.move()
    explore(hr, status)
    pprint(status)
    status = hr.move()
    explore(hr, status)
    pprint(status)
    status = hr.move()
    explore(hr, status)
    pprint(status)
    status = hr.move()
    explore(hr, status)
    pprint(status)
    status = hr.turn_anti_clockwise()
    explore(hr, status)
    pprint(status)
    status = hr.move()
    explore(hr, status)
    pprint(status)
    status = hr.move()
    explore(hr, status)
    pprint(status)
    status = hr.turn_clockwise()
    explore(hr, status)
    pprint(status)
    status = hr.move()
    explore(hr, status)
    pprint(status)
    status = hr.turn_clockwise()
    explore(hr, status)
    pprint(status)
    status = hr.move()
    explore(hr, status)
    pprint(status)

    pprint(hr.send_content({(0, 0): HC.EMPTY}))
    pprint(hr.send_content(complete_map_example))
    complete_map_example[(7, 0)] = HC.EMPTY
    pprint(hr.send_content(complete_map_example))

"""

if __name__ == "__main__":
    main()
