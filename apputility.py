from datetime import datetime
import re
from fuzzywuzzy import process


# List all restaurants that are open at a certain datetime format say: 02/10/2020 04:09 AM

def withinTimePeriod(startTime='03:00 PM', endTime='01:00 AM', checkTime='02:09 AM'):
    '''
    Checks if startTime <= checkTime < endTime
    :param startTime:
    :param endTime:
    :param checkTime:
    :return:
    '''
    # print (startTime, endTime, checkTime)
    timeStart = datetime.strptime (startTime, "%I:%M %p")
    timeEnd = datetime.strptime (endTime, "%I:%M %p")
    queryTime = datetime.strptime (checkTime, "%I:%M %p")

    if timeStart < timeEnd:
        return queryTime >= timeStart and queryTime < timeEnd
    else:  # Over midnight
        return queryTime >= timeStart or queryTime < timeEnd


def get_day(year=2012, month=1, day=23):
    '''
    Returns name of the day given year, month, day
    :param year:
    :param month:
    :param day:
    :return:
    '''
    week = ['Mon', 'Tues', 'Weds', 'Thurs', 'Fri', 'Sat', 'Sun', ]
    return week[datetime (year, month, day).weekday ()]


def isOpen(givenOpeningHours="Mon, Weds 5:15 am - 8:30 pm / Tues, Sat 1:30 pm - 3:45 pm", querydt="02/10/2020 04:09 AM"):
    '''
    Checks if restaurant is open or not.
    :param givenOpeningHours: opening days-hours in string format
    :param querydt: searched datetime for slot
    :return: True / False if slot is open
    '''

    if not givenOpeningHours:
        return None
    else:
        querydt_obj = datetime.strptime (querydt, '%d/%m/%Y %I:%M %p')
        query_day = get_day (year=querydt_obj.year, month=querydt_obj.month, day=querydt_obj.day)
        query_time = (querydt.split (' ', 1)[1]).strip ()

        # print (query_day)

        dtsplt = givenOpeningHours.split ('/')
        opening_schedule = {"": []}
        days = []

        for dt_dtr in dtsplt:
            # print('dt_dtr:', dt_dtr)
            dt_div =  [] #dt_dtr.split (':', 1)
            dt_div.append((dt_dtr[:(re.search (r"\d", dt_dtr)).start()]).strip())
            dt_div.append((dt_dtr[(re.search (r"\d", dt_dtr)).start():]).strip())

            # print('dt_div', dt_div)
            days = [x.strip () for x in (dt_div[0]).split (',')]


            # print(dt_div[1])

            st_end = dt_div[1].split ('-')
            st_end[0] = st_end[0].strip ()
            st_end[1] = st_end[1].strip ()
            if ':' not in st_end[0]:
                st_end[0] = ':00 '.join (st_end[0].split ())
            if ':' not in st_end[1]:
                st_end[1] = ':00 '.join (st_end[1].split ())
            # print(st_end[0], st_end[1])

            # start = datetime.strptime (st_end[0], "%I:%M %p")
            # end = datetime.strptime (st_end[1], "%I:%M %p")
            start = st_end[0].strip ()
            end = st_end[1].strip ()

            for day in days:
                # print('day', day)
                if not day in opening_schedule:
                    opening_schedule[day] = []
                opening_schedule[day].append ((start, end))

        # print ('query_day:', query_day)
        if query_day not in opening_schedule:
            # print ('h0')
            return False
        else:
            # print ('h1')
            open_times = opening_schedule[query_day]
            # print (open_times)
            for st, en in open_times:

                if withinTimePeriod (startTime=st, endTime=en, checkTime=query_time):
                    # print ('h2')
                    return True
    return False

def get_str_similarity(str2Match = "apple inc", strOptions = ["Apple Inc.", "apple park", "apple incorporated", "iphone"]):
    '''
    Get sorted ordered Levenshtein distance similarity
    :param str2Match:
    :param strOptions:
    :return:
    '''
    Ratios = process.extract (str2Match, strOptions)
    return Ratios


if __name__ == "__main__":
    # openingHours = "Mon, Weds 5:15 am - 8:30 pm / Tues, Sat 1:30 pm - 3:45 pm / Thurs 7:45 am - 8:15 am / Sun 12:45 pm - 6:15 pm"
    openingHours="Mon, Fri 2:30 pm - 8 pm / Tues 11 am - 2 pm / Weds 1:15 pm - 3:15 am / Thurs 10 am - 3:15 am / Sat 5 am - 11:30 am / Sun 10:45 am - 5 pm"
    myquerydt = "25/03/2022 03:45 PM"
    print (isOpen (givenOpeningHours=openingHours, querydt=myquerydt))
