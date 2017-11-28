# normally you'd just need the 'import oncall'
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import oncall

def main():
    # corresponds to python's .isoweekday method.
    # 1 is monday, 7 is sunday
    valid_days = (1, 2, 3, 4, 5) # for a weekday on call
    # valid_days = (6, 7) # for weekend on call
    # valid_days (1, 2, 3, 4, 5, 6, 7) # for an entire week on call
    
    # names of people.
    # will also autoload vacation info from [name].json if it exists ex: alice.json
    people = [ "alice", "bob", "carlos", "carol", "charlie", "dan", "eve", "steve" ]
    
    # pass in the year to calculate oncalls for, the list of valid days, and the list/
    oncalls = oncall.OnCallculator(2018, valid_days, people)

    # can use this to only calculate oncall for the first 10 weeks
    # oncalls = oncall.OnCallculator(2018, valid_days, people, 1, 10)

    oncalls.load_holidays("holidays.json")
    oncalls.calculate_oncall()
    print(oncalls)

if __name__ == "__main__":
    main()
