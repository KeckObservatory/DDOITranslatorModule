class DDOIArgumentsChangedException(Exception):
    pass


class DDOIKTLTimeoutException(Exception):
    pass


class DDOIMissingArgumentException(Exception):
    pass


class DDOISubsystemInactiveExcpetion(Exception):
    pass


class DDOISubsystemDisabledException(Exception):
    pass


class DDOIPreConditionNotRun(Exception):
    def __init__(self, class_name):
        self.message = f"Precondition was not run for {class_name}"
        super().__init__(self.message)

    def __str__(self):
        return f'{self.message}'


class DDOIArgumentsNotAdded(Exception):
    def __init__(self, class_name):
        self.message = f"Parser Arguments were not added for {class_name}"
        super().__init__(self.message)

    def __str__(self):
        return f'{self.message}'


class DDOIInvalidArguments(Exception):
    pass


class DDOIKTLTimeOut(Exception):
    pass


class DDOINoInstrumentDefined(Exception):
    pass


class DDOINotSelectedInstrument(Exception):
    def __init__(self, current_inst, inst):
        self.message = f"The selected instrument: {current_inst} is not {inst}"
        super().__init__(self.message)

    def __str__(self):
        return f'{self.message}'


class DDOIConfigException(Exception):
    def __init__(self, section, param_name):
        self.message = f"Check Config file, there is no parameter name: " \
                       f"{param_name} in section"
        super().__init__(self.message)

    def __str__(self):
        return f'{self.message}'


class DDOIConfigFileException(Exception):
    def __init__(self, param_type, match_type):
        self.message = f"Config parameter {param_type} is not a file path " \
                       f"or type: {match_type}"
        super().__init__(self.message)

    def __str__(self):
        return f'{self.message}'


class DDOIDetectorAngleUndefined(Exception):
    pass

