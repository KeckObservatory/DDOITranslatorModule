from ddoitranslatormodule.ddoiexceptions.DDOIExceptions import DDOIArgumentsChangedException, DDOIInvalidArguments, DDOIConfigFileException, DDOIConfigException, DDOIKTLTimeOut

from logging import getLogger
from argparse import ArgumentParser, Namespace, ArgumentTypeError
import configparser

import copy


# clean up the exceptions printed
def excepthook(type, value, traceback):
    print(f"Exception {type.__name__}: {value}")


#sys.excepthook = excepthook

help_str = ""


class TranslatorModuleFunction:
    """ 
    This is the base class for all Translator Module Functions at Keck.
    """
    
    # If True, then the abort_execution method may be invoked
    abortable = False
    help_string = help_str
    min_args = {}

    @classmethod
    def execute(cls, args, logger=None, cfg=None):
        """Carries out this function in its entirety (pre and post conditions
           included)

        Parameters
        ----------
        args : dict
            The OB (or portion of OB) in dictionary form
        logger : DDOILoggerClient, optional
            The DDOILoggerClient that should be used. If none is provided, defaults to
            a generic name specified in the config, by default None
        cfg : filepath, optional
            File path to the config that should be used, by default None

        Returns
        -------
        bool
            True if execution was sucessful, False otherwise

        Raises
        ------
        DDOIArgumentsChangedException
            If any changes to the input arguments are detected, this exception
            is raised. Code within a TranslatorModuleFunction should **NOT**
            change the input arguments
        """
        if type(args) == Namespace:
            args = vars(args)
        elif type(args) != dict:
            msg = "argument type must be either Dict or Argparser.Namespace"
            raise DDOIInvalidArguments(msg)

        # Access the logger and pass it into each method
        if logger is None:
            logger = getLogger("")

        # read the config file
        cfg = cls._load_config(cls, cfg, args=args)

        # Store a copy of the initial args
        initial_args = copy.deepcopy(args)

        # Check the pre-condition
        if not cls.pre_condition(args, logger, cfg):
            return False

        # Make sure that the pre-condition did not alter the arguments
        args_diff = cls._diff_args(args, initial_args)
        if args_diff:
            raise DDOIArgumentsChangedException(
                f"Arguments changed after executing pre-condition: {args_diff}")

        cls.perform(args, logger, cfg)
        args_diff = cls._diff_args(args, initial_args)
        if args_diff:
            raise DDOIArgumentsChangedException(
                f"Arguments changed after executing perform: {args_diff}")

        pst = cls.post_condition(args, logger, cfg)
        args_diff = cls._diff_args(args, initial_args)
        if args_diff:
            raise DDOIArgumentsChangedException(
                f"Arguments changed after executing post-condition: {args_diff}")
        return pst

    @classmethod
    def pre_condition(cls, args, logger, cfg):
      # pre-checks go here
      raise NotImplementedError()
          
    @classmethod
    def perform(cls, args, logger, cfg):
        # This is where the bulk of instrument code lives
        raise NotImplementedError()
    
    @classmethod
    def post_condition(cls, args, logger, cfg):
        # post-checks go here
        raise NotImplementedError()

    @classmethod
    def abort_execution(cls, args, logger, cfg):
        # Code to abort execution goes here
        raise NotImplementedError()

    @classmethod
    def abort(cls, args, logger=None, cfg=None):
        if logger is None:
            logger = getLogger("")

        if cls.abortable:
            cls.abort_execution(args, logger, cfg)
        else:
            logger.error("Failed to abort. abort_execution() is not enabled")

        # Code for shutting everything down, even while perform is operating
        raise NotImplementedError()

    @staticmethod
    def _diff_args(args1, args2):

        # Deep check if args1 == args2. This code may not be sufficient
        # return args1 != args2
        return False

    """
    Configuration File Read Section
    """
    def _load_config(cls, cfg, args=None):
        """
        Load the configuration file for reading

        @param cfg: <str> file path or None
        @param args: <dict> the class arguments

        @return: <class 'configparser.ConfigParser'> the config file parser.
        """
        config_files = []
        if not cfg:
            config_files = cls._cfg_location(cls, args)
            try:
                cfg = config_files[0]
            except (IndexError, TypeError):
                raise DDOIConfigFileException(config_files, list)

        # return if config object passed
        param_type = type(cfg)
        if param_type == configparser.ConfigParser:
            return cfg
        elif param_type != str:
            raise DDOIConfigFileException(param_type, configparser.ConfigParser)

        config = configparser.ConfigParser()
        config.read(config_files)

        return config

    def _cfg_location(cls, args):
        """
        Return the fullpath + filename of default configuration file.

        :param args: <dict> The OB (or portion of OB) in dictionary form

        :return: <list> list of paths + filename to config files
        """
        raise NotImplementedError()


    @staticmethod
    def _cfg_val(cfg, section, param_name):
        """
        Function used to read the config file,  and exit if key or value
        does not exist.

        @param cfg: <class 'configparser.ConfigParser'> the config file parser.
        @param section: <str> the section name in the config file.
        @param param_name: <str> the 'key' of the parameter within the section.
        @return: <str> the config file value for the parameter.
        """
        try:
            param_val = cfg[section][param_name]
        except KeyError:
            raise DDOIConfigException(section, param_name)

        if not param_val:
            raise DDOIConfigException(section, param_name)

        return param_val

    """
    Command line Argument Section for use with CLI (Command Line Interface)
    
        parser = argparse.ArgumentParser()
        args = Function.add_cmdline_args(parser)
        result = Function.execute(args)
    """
    @classmethod
    def add_cmdline_args(cls, parser, cfg=None):
        """
        The arguments to add to the command line interface.

        :param parser: <ArgumentParser>
            the instance of the parser to add the arguments to .
        :param cfg: <str> filepath, optional
            File path to the config that should be used, by default None

        :return: <ArgumentParser>
        """
        # add: return super().add_cmdline_args(parser, cfg) to the end of extended method
        parser.add_argument('-h', '--help', action='help', default='==SUPPRESS==',
                            help='show this help message and exit')

        return parser

    @staticmethod
    def _add_args(parser, args_to_add, print_only=False):
        """
        Add the argparse arguments.

        :param parser: <configparser> The parser object
        :param args_to_add: OrderedDict the arguments to add.
            keywords:
                'help' - <str> the help string to add, required
                'type' - <python type>, the argument type,  required
                'req' - <bool> True if the argument is required,  optional
                'kw_arg' - <bool> True for keyword arguments, optional
        :param print_only: <bool> True if add the print_only option

        :return: <configparser> The parser object
        """
        # check to see if print_only is true,  then do not add other arguments.
        if print_only:
            parser.add_argument('--print_only', action='store_true', default=False)
            args = parser.parse_known_args()
            if args[0].print_only:
                return parser

        for arg_name, arg_info in args_to_add.items():
            # add keyword arguments
            if 'kw_arg' in arg_info and arg_info['kw_arg']:
                parser.add_argument(f'--{arg_name}', type=arg_info['type'],
                                    required=arg_info['req'], help=arg_info['help'])
                continue

            # add positional arguments
            parser.add_argument(arg_name, type=arg_info['type'], help=arg_info['help'])

        return parser

    @staticmethod
    def _add_bool_arg(parser, name, msg, default=None):
        """

        :param parser: <configparser> The parser object.
        :param name: <str> the parameter name
        :param msg: <str> the help message

        :return: <configparser> The parser object.
        """

        def _str_to_bool(arg_val, name):
            if isinstance(arg_val, bool):
                return arg_val

            if arg_val.lower() in ('yes', 'true', 't', 'y', '1'):
                return True
            elif arg_val.lower() in ('no', 'false', 'f', 'n', '0'):
                return False
            else:
                raise ArgumentTypeError(f'Boolean value expected for: {name}.')

        if not default:
            arg_default = False

        parser.add_argument(f'--{name}', action='store_true', type=_str_to_bool,
                            default=arg_default, help=msg)
        return parser

