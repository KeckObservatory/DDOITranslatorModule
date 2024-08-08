##-------------------------------------------------------------------------
## Define some exceptions
##-------------------------------------------------------------------------
##
## --> Need to sort out logging <--
##
class TranslatorException(Exception):
    def __init__(self, message=""):
        self.message = message
        log.error(self.message)
        super().__init__(self.message)


class FailedPreCondition(TranslatorException):
    def __init__(self, pcmessage=""):
        self.pcmessage = f"Failed PreCondition: {pcmessage}"
        super().__init__(self.pcmessage)


class FailedPostCondition(TranslatorException):
    def __init__(self, pcmessage=""):
        self.pcmessage = f"Failed PostCondition: {pcmessage}"
        super().__init__(self.pcmessage)


class FailedToReachDestination(FailedPostCondition):
    def __init__(self, value="", destination="", ):
        self.destination = destination
        self.value = value
        msg = f"Current value ({value}) != destination ({destination})"
        super().__init__(msg)
