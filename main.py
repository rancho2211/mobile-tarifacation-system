import time
import datetime
from event import *

event_history = EventList()
event_history.add(TopUpEvent(time.time(), 400))
event_history.add(TopUpEvent(time.time(), 400))
event_history.add(IncomingCallEvent(952041600, "89093465434", 76))
event_history.add(IncomingCallEvent(952041600, "89093465434", 76))
event_history.add(IncomingCallEvent(time.time(), "89098635162", 42))
event_history.add(IncomingCallEvent(time.time(), "89093435162", 50))
event_history.add(RoamingEnterEvent(564564564))
event_history.add(IncomingCallEvent(time.time(), "89093465434", 76))
event_history.add(IncomingCallEvent(time.time(), "89098635162", 42))
event_history.add(OutgoingCallEvent(time.time(), "89098635162", 38))
event_history.add(IncomingSMSEvent(time.time(), "89098635162", "Hi this is an important message"))
event_history.add(OutgoingSMSEvent(time.time(), "89098635162", "Okey"))
event_history.add(MobileInternetEvent(time.time(), 54))
event_history.add(RoamingExitEvent(time.time()))
event_history.add(MobileInternetEvent(time.time(), 30))
event_history.add(MobileInternetEvent(time.time(), 54))
event_history.update_roaming()

while True:
    request_input = raw_input("Enter month and year: ")
    month, year = request_input.split('.', )
    month = int(month)
    year = int(year)
    if month > 12 or month < 1 or year > 2020 or year < 1970:
        print "Incorrect date. Try again!"
        continue
    d = datetime.date(year, month, 1)
    SEC_PER_MONTH = 2629743
    next_year = False
    if month == 12:
        next_year = True
    next_d = datetime.date(year + 1, 1, 1) if next_year else datetime.date(year, month + 1, 1)
    start_date = time.mktime(d.timetuple())
    finish_date = time.mktime(next_d.timetuple())
    if not event_history.check_date(start_date, finish_date):
        print "No data found"
        continue
    event_history.print_detalization(start_date, finish_date)
