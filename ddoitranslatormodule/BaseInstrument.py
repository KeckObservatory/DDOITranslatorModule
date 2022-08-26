from ddoitranslatormodule.BaseFunction import TranslatorModuleFunction
import os


class InstrumentBase(TranslatorModuleFunction):

    def _cfg_location(cls, args):
        """
        Return the fullpath + filename of default configuration file.

        :param args: <dict> The OB (or portion of OB) in dictionary form

        :return: <list> fullpath + filename of default configuration
        """
        cfg_path_base = os.path.dirname(os.path.abspath(__file__))

        try:
            inst = cls.inst
        except NameError:
            if args:
                inst = args.get('instrument', None)
            else:
                inst = cls.read_current_inst(None)

        cfg = f"{cfg_path_base}/ddoi_configurations/{inst}_inst_config.ini"
        config_files = [cfg]

        return config_files


