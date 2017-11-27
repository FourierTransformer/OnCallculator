# OnCallculator
The OnCallculator can create simple on call call calendars for people to use. It has been tested and working on python 2.7 and 3.6 (it should work with most versions).

# Usage
After installing the module (or cloning the repo and modifying the example directory), you can easily get setup and going. It takes in a few things as external inputs:

 * a list of holidays (ex: [example/holidays.json](example/holidays.json))
 * each person's individual vacation preferences and previous holiday information (ex: [example/alice.json](example/alice.json))

A list of holidays can be sent in. The OnCallculator will ensure that different people will be assigned on holidays and, if there are more holidays than people, that the holidays assigned will be spread out. People can also list previous holidays they were assigned to ensure that they will not be assigned again.

# Known Bugs
There are a few fun bugs, but are easy to get around:
 * The previous holidays don't take in a year, and assume the year passed to the constructor. For holidays that change date (like Thanksgiving) put the date for the passed in year. Ex: Alice worked Thanksgiving 2017 (11/23/2017), but Thanksgiving is on 11/22 in 2018, so for her "previousHoliday" would list 11/22. Now, as long as the week it occurs on is the same, this isn't an issue - but that might not always line up.
 * The ISO calendar for the year may or may not line up with your on-call schedule. It should work for 2018! This could be a little annoying to account for in the future. Pull Requests welcome.
 * Since there is a greedy preference for spreading out holidays and preferring vacations, people can be assigned two weeks in a row. In the example output below, bob is assigned on week 46 and 47 (Thanksgiving), as everyone else (except Alice) already has been assigned a holiday. Alice worked Thanksgiving last year, so she wont get it again. This is a forced example, but could happen in real life. It's up to bob to now find a replacement.

# Example code
(example/oncalls.py)[example/oncalls.py]:

``` python
import oncall

def main():
    # corresponds to python's .isoweekday method.
    # 1 is monday, 7 is sunday
    valid_days = (1, 2, 3, 4, 5) # for a weekday on call
    # valid_days = (6, 7) # for weekend on call
    # valid_days (1, 2, 3, 4, 5, 6, 7) # for an entire week on call
    
    # names of people.
    # it will follow this order until a vacation/previous holiday gets in the way
    # will also autoload vacation info form [name].json ex: alice.json
    people = [ "alice", "bob", "carlos", "carol", "charlie", "dan", "eve", "steve" ]
    
    # pass in the year, the list of valid days, and the list/
    oncalls = oncall.OnCallculator(2018, valid_days, people)
    oncalls.load_holidays("holidays.json")
    oncalls.calculate_oncall()
    print(oncalls)

if __name__ == "__main__":
    main()
```

Run the example!
```
cd example
python oncalls.py
```

Example Output:
```
OnCallculator Calendar
1   carol   01/01 - 01/05   (holiday)
2   alice   01/08 - 01/12
3   carlos  01/15 - 01/19   (holiday)
4   bob 01/22 - 01/26
5   charlie 01/29 - 02/02
6   dan 02/05 - 02/09
7   eve 02/12 - 02/16
8   steve   02/19 - 02/23   (holiday)
9   carol   02/26 - 03/02
10  alice   03/05 - 03/09
11  carlos  03/12 - 03/16
12  charlie 03/19 - 03/23
13  dan 03/26 - 03/30
14  eve 04/02 - 04/06
15  bob 04/09 - 04/13
16  steve   04/16 - 04/20
17  carol   04/23 - 04/27
18  alice   04/30 - 05/04
19  carlos  05/07 - 05/11
20  charlie 05/14 - 05/18
21  dan 05/21 - 05/25
22  eve 05/28 - 06/01   (holiday)
23  bob 06/04 - 06/08
24  steve   06/11 - 06/15
25  alice   06/18 - 06/22
26  carlos  06/25 - 06/29
27  charlie 07/02 - 07/06   (holiday)
28  carol   07/09 - 07/13
29  dan 07/16 - 07/20
30  bob 07/23 - 07/27
31  eve 07/30 - 08/03
32  steve   08/06 - 08/10
33  alice   08/13 - 08/17
34  carlos  08/20 - 08/24
35  charlie 08/27 - 08/31
36  dan 09/03 - 09/07   (holiday)
37  carol   09/10 - 09/14
38  bob 09/17 - 09/21
39  eve 09/24 - 09/28
40  steve   10/01 - 10/05
41  alice   10/08 - 10/12
42  carlos  10/15 - 10/19
43  charlie 10/22 - 10/26
44  dan 10/29 - 11/02
45  carol   11/05 - 11/09
46  bob 11/12 - 11/16
47  bob 11/19 - 11/23   (holiday)
48  eve 11/26 - 11/30
49  steve   12/03 - 12/07
50  alice   12/10 - 12/14
51  carlos  12/17 - 12/21
52  charlie 12/24 - 12/28   (holiday)

Total Oncalls:
dan: 6
carol: 6
bob: 7
eve: 6
steve: 6
alice: 7
carlos: 7
charlie: 7

Final Order
['dan', 'carol', 'bob', 'eve', 'steve', 'alice', 'carlos', 'charlie']
```
