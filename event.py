import math

SEC_PER_MIN = 60.0
INCOMING_CALLS_IN_ROAMING = 8
INCOMING_CALLS_IN_HOME = 0
FREE_CALLS_DURATION = 3
OUTGOING_CALLS_IN_ROAMING = 20
OUTGOING_CALLS_IN_HOME = 2
OUTGOING_SMS_SYMBOLS = 70.0
OUTGOING_SMS_IN_ROAMING = 5
OUTGOING_SMS_IN_HOME = 1
TRANSFERRED_IN_ROAMING = 5
TRANSFERRED_IN_HOME = 0.2

class Event(object):

    def __init__(self, ts):
        self.ts = ts
        self.is_roaming = False

    def set_roaming(self, value):
        self.is_roaming = value

    def get_recharge(self):
        raise NotImplementedError()

    def get_expensis(self):
        raise NotImplementedError()

class TopUpEvent(Event):

    def __init__(self, ts, count):
        super(TopUpEvent, self).__init__(ts)
        self.count = count

    def get_recharge(self):
        return self.count

    def get_expensis(self):
        return 0
    

class IncomingCallEvent(Event):

    def __init__(self, ts, phone_number, duration):
        super(IncomingCallEvent, self).__init__(ts)
        self.phone_number = phone_number
        self.duration = duration

    def get_recharge(self):
        return 0

    def get_expensis(self):
        if self.is_roaming:
            return math.ceil(self.duration / SEC_PER_MIN) * INCOMING_CALLS_IN_ROAMING
        return math.ceil(self.duration / SEC_PER_MIN) * INCOMING_CALLS_IN_HOME

class OutgoingCallEvent(Event):

    def __init__(self, ts, phone_number, duration):
        super(OutgoingCallEvent, self).__init__(ts)
        self.phone_number = phone_number
        self.duration = duration

    def get_recharge(self):
        return 0

    def get_expensis(self):
        if self.duration <= FREE_CALLS_DURATION:
            return 0
        elif self.is_roaming:
            return math.ceil(self.duration / SEC_PER_MIN) * OUTGOING_CALLS_IN_ROAMING
        return math.ceil(self.duration / SEC_PER_MIN) * OUTGOING_CALLS_IN_HOME

class IncomingSMSEvent(Event):

    def __init__(self, ts, phone_number, content):
        super(IncomingSMSEvent, self).__init__(ts)
        self.phone_number = phone_number
        self.content = content

    def get_recharge(self):
        return 0

    def get_expensis(self):
        return 0

class OutgoingSMSEvent(Event):

    def __init__(self, ts, phone_number, content):
        super(OutgoingSMSEvent, self).__init__(ts)
        self.phone_number = phone_number
        self.content = content

    def get_recharge(self):
        return 0

    def get_expensis(self):
        if self.is_roaming:
            return math.ceil(len(self.content) / OUTGOING_SMS_SYMBOLS) * OUTGOING_SMS_IN_ROAMING
        return math.ceil(len(self.content) / OUTGOING_SMS_SYMBOLS) * OUTGOING_SMS_IN_HOME

class MobileInternetEvent(Event):

    def __init__(self, ts, megabytes):
        super(MobileInternetEvent, self).__init__(ts)
        self.megabytes = megabytes

    def get_recharge(self):
        return 0

    def get_expensis(self):
        if self.is_roaming:
            return math.ceil(self.megabytes * TRANSFERRED_IN_ROAMING)
        return math.ceil(self.megabytes * TRANSFERRED_IN_HOME)

class RoamingEnterEvent(Event):

    def __init__(self, ts):
        super(RoamingEnterEvent, self).__init__(ts)

    def get_recharge(self):
        return 0

    def get_expensis(self):
        return 0

class RoamingExitEvent(Event):

    def __init__(self, ts):
        super(RoamingExitEvent, self).__init__(ts)

    def get_recharge(self):
        return 0

    def get_expensis(self):
        return 0


class EventList(object):

    def __init__(self):
        self.list = []

    def add(self, event):
        self.list.append(event)

    def remove(self, event):
        self.list.remove(event)

    def check_date(self, _from, _to):
        for event in self.list:
            if event.ts >= _from and event.ts <= _to:
                return True
        return False

    def check_event_date(self, event, _from, _to):
        return event.ts >= _from and event.ts <= _to

    def update_roaming(self):
        is_roaming_active = False
        for event in self.list:
            if isinstance(event, RoamingEnterEvent):
                is_roaming_active = True
            if isinstance(event, RoamingExitEvent):
                is_roaming_active = False
            event.is_roaming = is_roaming_active

    def get_recharge(self, _from, _to):
        return sum(event.get_recharge() for event in self.list if self.check_event_date(event, _from, _to))

    def get_expensis(self, _from, _to):
        return sum(event.get_expensis() for event in self.list if self.check_event_date(event, _from, _to))

    def print_detalization(self, _from, _to):
        print "Total recharge: {0} RUB".format(self.get_recharge(_from, _to))
        print "Total expenses: {0} RUB".format(self.get_expensis(_from, _to))
        print "Detalization:"
        
        incoming_calls = sum (1 for event in self.list if self.check_event_date(event, _from, _to) and isinstance(event, IncomingCallEvent) and not event.is_roaming)
        total_length = sum(math.ceil(event.duration / SEC_PER_MIN) for event in self.list if self.check_event_date(event, _from, _to) and isinstance(event, IncomingCallEvent) and not event.is_roaming)
        charged = math.ceil(sum(event.get_expensis() for event in self.list if self.check_event_date(event, _from, _to) and isinstance(event, IncomingCallEvent) and not event.is_roaming))
        print "Incoming calls (home net): {0}, total length: {1} min, charged: {2} RUB".format(incoming_calls, total_length, charged)
        
        incoming_calls = sum (1 for event in self.list if self.check_event_date(event, _from, _to) and isinstance(event, IncomingCallEvent) and event.is_roaming)
        total_length = sum(math.ceil(event.duration / SEC_PER_MIN) for event in self.list if self.check_event_date(event, _from, _to) and isinstance(event, IncomingCallEvent) and event.is_roaming)
        charged = math.ceil(sum(event.get_expensis() for event in self.list if self.check_event_date(event, _from, _to) and  isinstance(event, IncomingCallEvent) and event.is_roaming))
        print "Incoming calls (roaming): {0}, total length: {1} min, charged: {2} RUB".format(incoming_calls, total_length, charged)

        outgoing_calls = sum (1 for event in self.list if self.check_event_date(event, _from, _to) and isinstance(event, OutgoingCallEvent) and not event.is_roaming)
        total_length = sum(math.ceil(event.duration / SEC_PER_MIN) for event in self.list if self.check_event_date(event, _from, _to) and isinstance(event, OutgoingCallEvent) and not event.is_roaming)
        charged = math.ceil(sum(event.get_expensis() for event in self.list if self.check_event_date(event, _from, _to) and isinstance(event, OutgoingCallEvent) and not event.is_roaming))
        print "Outgoing calls (home net): {0}, total length: {1} min, charged: {2} RUB".format(outgoing_calls, total_length, charged)

        outgoing_calls = sum (1 for event in self.list if self.check_event_date(event, _from, _to) and isinstance(event, OutgoingCallEvent) and event.is_roaming)
        total_length = sum(math.ceil(event.duration / SEC_PER_MIN) for event in self.list if self.check_event_date(event, _from, _to) and isinstance(event, OutgoingCallEvent) and event.is_roaming)
        charged = math.ceil(sum(event.get_expensis() for event in self.list if self.check_event_date(event, _from, _to) and isinstance(event, OutgoingCallEvent) and event.is_roaming))
        print "Outgoing calls (roaming): {0}, total length: {1} min, charged: {2} RUB".format(outgoing_calls, total_length, charged)

        incoming_sms = sum (1 for event in self.list if self.check_event_date(event, _from, _to) and isinstance(event, IncomingSMSEvent))
        charged = math.ceil(sum(event.get_expensis() for event in self.list if self.check_event_date(event, _from, _to) and isinstance(event, IncomingSMSEvent)))
        print "Incoming SMS: {0}, charged: {1} RUB".format(incoming_sms, charged)

        outgoing_sms = sum (1 for event in self.list if self.check_event_date(event, _from, _to) and isinstance(event, OutgoingSMSEvent) and not event.is_roaming)
        charged = math.ceil(sum(event.get_expensis() for event in self.list if self.check_event_date(event, _from, _to) and isinstance(event, OutgoingSMSEvent) and not event.is_roaming))
        print "Outgoing SMS(home net): {0}, charged: {1} RUB".format(outgoing_sms, charged)

        outgoing_sms = sum (1 for event in self.list if self.check_event_date(event, _from, _to) and isinstance(event, OutgoingSMSEvent) and event.is_roaming)
        charged = math.ceil(sum(event.get_expensis() for event in self.list if self.check_event_date(event, _from, _to) and isinstance(event, OutgoingSMSEvent) and event.is_roaming))
        print "Outgoing SMS(roaming): {0}, charged: {1} RUB".format(outgoing_sms, charged)

        mobile_internet = sum (event.megabytes for event in self.list if self.check_event_date(event, _from, _to) and isinstance(event, MobileInternetEvent) and not event.is_roaming)
        charged = math.ceil(sum(event.get_expensis() for event in self.list if self.check_event_date(event, _from, _to) and isinstance(event, MobileInternetEvent) and not event.is_roaming))
        print "Mobile internet(home net): {0} Mb, charged: {1} RUB".format(mobile_internet, charged)

        mobile_internet = sum (event.megabytes for event in self.list if self.check_event_date(event, _from, _to) and isinstance(event, MobileInternetEvent) and event.is_roaming)
        charged = math.ceil(sum(event.get_expensis() for event in self.list if self.check_event_date(event, _from, _to) and isinstance(event, MobileInternetEvent) and event.is_roaming))
        print "Mobile internet(roaming): {0} Mb, charged: {1} RUB".format(mobile_internet, charged)
