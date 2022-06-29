from ddoitranslatormodule.ddoiexceptions.DDOIExceptions import DDOIArgumentsChangedException, DDOIInvalidArguments
from logging import getLogger
from argparse import Namespace
import configparser

import copy
import sys
import ktl


# clean up the exceptions printed
def excepthook(type, value, traceback):
    print(f"{type.__name__}: {value}")


sys.excepthook = excepthook

help = ""



class TranslatorModuleFunction:
    """ 
    This is the base class for all Translator Module Functions at Keck.
    """
    
    # If True, then the abort_execution method may be invoked
    abortable = False
    help_string = help
    min_args = {}

    @classmethod
    def execute(cls, args, logger=None, cfg=None):
        """Carries out this function in its entirety (pre and post conditions
           included)

        Parameters
        ----------
        args : dict
            The OB in dictionary form
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

        if cfg:
            # cfg_path = os.path.dirname(os.path.abspath(__file__))
            # cfg = cls._load_config(f"{cfg_path}/{cfg}")
            cfg = cls._load_config(f"{cfg}")

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

    @staticmethod
    def _load_config(cfg):
        config = configparser.ConfigParser()
        config.read(cfg)

        return config

    @classmethod
    def add_cmdline_args(cls, parser, cfg):
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
        args = parser.parse_args()

        return args


