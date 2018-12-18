from icalendar import Calendar, Event
import time
import datetime
import json

def convert_string_to_date(str, year, date_format="%m/%d"):
    new_date = datetime.datetime.strptime(str, date_format)
    return new_date.replace(year=year)

def get_week_number(date):
    return date.isocalendar()[1]

def load_json_file(filename):
    print("Loading {0}...".format(filename))
    file_contents = open(filename).read()
    return json.loads(file_contents)

def iso_to_gregorian(iso_year, iso_week, iso_day):
    fourth_jan = datetime.date(iso_year, 1, 4)
    _, fourth_jan_week, fourth_jan_day = fourth_jan.isocalendar()
    return fourth_jan + datetime.timedelta(days=iso_day-fourth_jan_day, weeks=iso_week-fourth_jan_week)

class Week:
    def __init__(self, week, valid_days, year):
        self.week = week
        self.holiday_week = False
        self.on_call = None
        
        # come up with a nice string
        self.start_day = iso_to_gregorian(year, week, valid_days[0])
        self.end_day = iso_to_gregorian(year, week, valid_days[-1])
        self.string_range = self.start_day.strftime("%m/%d") + " - "
        self.string_range = self.string_range + self.end_day.strftime("%m/%d")

    def __str__(self):
        output = "{0}\t{1}\t{2}".format(self.week, self.on_call, self.string_range)
        if self.holiday_week:
            output = output + "\t(holiday)"
        return output

class OnCallPerson:
    def __init__(self, id, year, valid_days):
        self.id = id
        self.avoid_weeks = set([])
        self.assigned_holiday = False
        self.oncalls = 0
        self.dates = []

        # try to the load the file if it exists
        try:
            person_info = load_json_file(id + ".json")
        except IOError:
            pass
        else:
            if "vacations" in person_info:
                self.parse_date_range(person_info["vacations"], year, valid_days, track=True)

            if "previousHolidays" in person_info:
                self.parse_date_range(person_info["previousHolidays"], year, valid_days)

    def parse_date_range(self, inputs, year, valid_days, track=False):
        for dates in inputs:
            # handle ranges specified
            if "-" in dates:
                # print("\nfound range:")
                dates_range = [x.strip() for x in dates.split("-")]
                dates_day = convert_string_to_date(dates_range[0], year)
                dates_end = convert_string_to_date(dates_range[1], year)
                if track:
                    self.dates.append((dates_day, dates_end))
                # print(dates_day)
                # print(dates_end - dates_day)
                # iterate over dates days, 
                while dates_day <= dates_end:
                    if dates_day.isoweekday() in valid_days:
                        dates_week_num = get_week_number(dates_day)
                        self.avoid_weeks.add(dates_week_num)    
                    dates_day = dates_day + datetime.timedelta(days=1)
            else:
                dates_date = convert_string_to_date(dates, year)
                if track:
                    self.dates.append((dates_date, dates_date))
                if dates_date.isoweekday() in valid_days:
                    dates_week_num = get_week_number(dates_date)
                    self.avoid_weeks.add(dates_week_num)
            

class OnCallculator:

    def __init__(self, year, valid_days, oncall_ids, start_week=1, end_week=52, name="Oncall"):
        self.year = year
        self.valid_days = valid_days
        self.name = name

        # intialize the weeks
        self.weeks = [Week(x, valid_days, year) for x in range(0, 53)]
        self.weeks[0] = None # there is no week 0...

        self.oncall_people = [OnCallPerson(x, year, valid_days) for x in oncall_ids]

        # keep track of how much we need to do
        self.start_range = start_week
        self.end_range = end_week + 1

    def load_holidays(self, holiday_file):
        # load up the holidays json file.
        holidays = load_json_file(holiday_file)
        for holiday in holidays["holidays"]:
            holiday_date = convert_string_to_date(holiday, self.year)
            if holiday_date.isoweekday() in self.valid_days:
                holiday_week_num = get_week_number(holiday_date)
                self.weeks[holiday_week_num].holiday_week = True

    def find_suitable_person(self, week_num):
        # try to find out the best person for the job
        selected_index = None
        selected_person = None

        # iterate over people to find someone suitable
        for j, person in enumerate(self.oncall_people):
            if not (
                (week_num in person.avoid_weeks) or 
                (self.weeks[week_num].holiday_week and person.assigned_holiday)
            ):
                selected_index = j
                selected_person = person
                break

        selected_person.oncalls = selected_person.oncalls+1

        return selected_index, selected_person

    def calculate_oncall(self):
        # iterate over the week as nums
        for i in range(self.start_range, self.end_range):
            # try to find out the best person for the job
            selected_index = None
            selected_person = None
            selected_index, selected_person = self.find_suitable_person(i)

            # gotta do some cleanup if all the holidays are taken
            if selected_index is None:
                # this can happen if there are too many holidays,
                # and not enough people.
                # just gotta clear them and keep going
                for x in self.oncall_people:
                    x.assigned_holiday = False

                selected_index, selected_person = self.find_suitable_person(i)


            # set the on call person for the week
            self.weeks[i].on_call = selected_person.id

            # remove the on call person and add them to the end of the list
            oncall_person = self.oncall_people.pop(selected_index)
            if self.weeks[i].holiday_week:
                oncall_person.assigned_holiday = True
            self.oncall_people.append(oncall_person)

    def generate_ics(self, show_peoples_vacation=True):
        cal = Calendar()
        cal.add('prodid', '-//OnCallculator//v2//')
        cal.add('version', '2.0') # this is the ics version. don't change this.
        for i in range(self.start_range, self.end_range):
            event = Event()
            event.add("summary", "{0}: {1}".format(self.name, self.weeks[i].on_call))
            event.add('dtstart', self.weeks[i].start_day)
            # not sure if dtend is inclusive, but outlook displays it incorrectly, so adding a day
            event.add('dtend', self.weeks[i].end_day+datetime.timedelta(days=1))
            event.add('dtstamp', datetime.datetime.utcnow())
            cal.add_component(event)
        
        if show_peoples_vacation:
            for person in self.oncall_people:
                for vacation in person.dates:
                    event = Event()
                    event.add("summary", "{0} OOO".format(person.id))
                    event.add('dtstart', vacation[0])
                    # not sure if dtend is inclusive, but outlook displays it incorrectly, so adding a day
                    event.add('dtend', vacation[1]+datetime.timedelta(days=1))
                    event.add('dtstamp', datetime.datetime.utcnow())
                    cal.add_component(event)
        
        return cal.to_ical()


    def __str__(self):
        # throw all the output in here.
        output = ["OnCallculator Calendar"]

        # iterate over the weeks
        for i in range(self.start_range, self.end_range):
            output.append(str(self.weeks[i]))

        # print out the numbers
        output.append("\nTotal Oncalls:")
        for person in self.oncall_people:
            output.append("{0}: {1}".format(person.id, person.oncalls))

        # show the final ordering
        output.append("\nFinal Order")
        people = [person.id for person in self.oncall_people]
        output.append(str(people))

        return '\n'.join(output)

