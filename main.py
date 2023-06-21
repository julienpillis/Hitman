from hitman.hitman import HC
from phase1 import *
from phase2 import *
from pprint import pprint


def phase1_run(hr):
    status = hr.start_phase1()
    launch_exploration(status,hr)

def phase2_run(hr,map):
    status = hr.start_phase2()
    launch_killing(status,hr,map)

def main():
    hr = HitmanReferee()
    status = hr.start_phase1()
    pprint(status)
    phase1_run(hr)
    _, score, history, true_map = hr.end_phase1()
    pprint(score)
    pprint(true_map)
    pprint(history)

    hr = HitmanReferee()
    status = hr.start_phase2()
    pprint(status)
    phase2_run(hr,true_map)
    _, score, history = hr.end_phase2()
    pprint(score)
    pprint(history)


if __name__ == "__main__":
    main()



