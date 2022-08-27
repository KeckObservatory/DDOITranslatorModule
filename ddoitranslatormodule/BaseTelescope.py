from ddoitranslatormodule.BaseFunction import TranslatorModuleFunction
from ddoitranslatormodule.ddoiexceptions.DDOIExceptions import DDOIConfigFileException, DDOIConfigException, DDOIInvalidArguments, DDOIKTLTimeOut
from ddoitranslatormodule.ddoiexceptions.DDOIExceptions import DDOINotSelectedInstrument, DDOINoInstrumentDefined

import os
import ktl


class TelescopeBase(TranslatorModuleFunction):

    def _cfg_location(cls, args):
        """
        Return the fullpath + filename of default configuration file.

        :param args: <dict> The OB (or portion of OB) in dictionary form

        :return: <list> fullpath + filename of default configuration
        """
        cfg_path_base = os.path.dirname(os.path.abspath(__file__))
        cfg = f"{cfg_path_base}/ddoi_configurations/default_tel_config.ini"
        config_files = [cfg]
        if args:
            inst = args.get('instrument', None)
        else:
            inst = cls.read_current_inst(None)

        if not inst:
            return config_files

        file_name = f"{inst.lower()}_tel_config.ini"
        cfg = f"{cfg_path_base}/ddoi_configurations/{file_name}"
        if os.path.exists(cfg):
            config_files.append(cfg)

        return config_files

    def _add_inst_arg(cls, parser, cfg, is_req=True):
        """
        Add Instrument as a command line argument.

        :param parser: <configparser> The parser object.
        :param cfg: <class 'configparser.ConfigParser'> the config file parser.
        :param is_req: <bool> if the parameter is required or not

        :return: <configparser> The parser object.
        """
        insts = cls._cfg_val(cfg, 'inst_list', 'insts')
        insts = f'{insts}, {insts.lower()}'
        inst_set = set(insts.split(', '))

        help_str = "Name of instrument for the translator module."
        parser.add_argument("--instrument", type=str, choices=inst_set,
                            required=is_req, help=help_str)

        return parser

    @staticmethod
    def _get_arg_value(args, key):
        """
        Check the provided arguments for the 'key' values.

        :param args: <dict> the command arguments
        :param key: <str> the dictionary key

        :return: The value of the parameter
        """
        val = args.get(key, None)

        if val is None:
            msg = f'{key} argument not defined'
            raise DDOIInvalidArguments(msg)

        return val

    def get_inst_name(cls, args, cfg, allow_current=True):
        """
        Get the instrument name from the arguments,  if not defined get from
        DCS current instrument.  If allow_current=False,  raise
        DDOINoInstrumentDefined if not defined in arguments.  allow_current=True
        allows the command to be run without a need to define the instrument,
        and using the instrument selected by the TCS.

        :param args: <dict> the arguments passed to calling function
        :param class_name: the name of the calling class for exception

        :return: <str> the instrument name
        """
        inst = args.get('instrument', None)
        if inst:
            # confirm INST = the selected instrument
            current_inst = cls.read_current_inst(cls, cfg)
            if current_inst != inst:
                raise DDOINotSelectedInstrument(current_inst, inst.upper())
            return inst.lower()

        if allow_current:
            inst = cls.read_current_inst(cls, cfg)
        else:
            msg = f'{cls.__name__} requires instrument name to be defined'
            raise DDOINoInstrumentDefined(msg)

        return inst.lower()

    def read_current_inst(cls, cfg):
        """
        Determine the current selected instrument

        :param cfg:
        :return:
        """
        if cfg:
            ktl_instrument = cls._cfg_val(cfg, 'ktl_kw_dcs', 'instrument')
            serv_name = cls._cfg_val(cfg, 'ktl_serv', 'dcs')
        else:
            ktl_instrument = 'instrume'
            serv_name = 'dcs'

        try:
            inst = ktl.read(serv_name, ktl_instrument, timeout=2)
        except ktl.TimeoutException:
            msg = f'timeout reading,  service {serv_name}, ' \
                  f'keyword: {ktl_instrument}'
            raise DDOIKTLTimeOut(msg)

        return inst.lower()

    @staticmethod
    def write_msg(logger, msg, print_only=False):
        """
        Write a message to logger if defined,  or to stdout if print_only
        or logger is not defined.

        :param logger: <DDOILoggerClient>, optional
                The DDOILoggerClient that should be used. If none is provided,
                defaults to a generic name specified in the config, by
                default None
        :param msg: <str> the message to write
        :param print_only: <bool> True if it is meant to be printed to stdout
        """
        # if logger instance,  write to the log
        if logger:
            logger.info(msg)

        # print to stdout for 'print_only'
        if print_only:
            print(msg)
