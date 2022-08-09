from ddoitranslatormodule.BaseFunction import TranslatorModuleFunction


class InstrumentBase(TranslatorModuleFunction):

    def _config_location(cls, args):
        """
        Return the fullpath + filename of default configuration file.

        :param args: <dict> The OB (or portion of OB) in dictionary form

        :return: <list> fullpath + filename of default configuration
        """
        raise NotImplementedError()


