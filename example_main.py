from hitman.hitman import HC, HitmanReferee, complete_map_example, world_example
from pprint import pprint
from constraints import *






def main():


    hr = HitmanReferee()
    status = hr.start_phase1()
    #pprint(status)
    launch_solving(status['m'],status['n'],status['guard_count'],status['civil_count'])
    explore(hr,status)
"""
    
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
