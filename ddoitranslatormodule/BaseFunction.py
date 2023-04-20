from ddoitranslatormodule.ddoiexceptions.DDOIExceptions import *

from logging import getLogger
from argparse import Namespace, ArgumentTypeError
import configparser
import traceback
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


        #################
        # PRE CONDITION #
        #################
        try:
            cls.pre_condition(args, logger, cfg)
        except Exception as e:
            logger.error(f"Exception encountered in pre-condition: {e}", exc_info=True)
            raise DDOIPreConditionFailed()
        
        args_diff = cls._diff_args(initial_args, args)

        if args_diff:
            logger.error(f"Args changed after pre-condition!")
            raise DDOIArgumentsChangedException(f"Args changed after pre-condition")


        ###########
        # EXECUTE #
        ###########
        
        try:
            return_value = cls.perform(args, logger, cfg)
        except Exception as e:
            logger.error(f"Exception encountered in perform: {e}", exc_info=True)
            raise DDOIPerformFailed()
        
        args_diff = cls._diff_args(initial_args, args)

        if args_diff:
            logger.error(f"Args changed after perform!")
            raise DDOIArgumentsChangedException(f"Args changed after pre-condition")
        

        ##################
        # POST CONDITION #
        ##################

        try:
            cls.post_condition(args, logger, cfg)
        except Exception as e:
            logger.error(f"Exception encountered in post-condition: {e}")
            logger.error(traceback.format_exc(), exc_info=True)
            raise DDOIPostConditionFailed()
        
        args_diff = cls._diff_args(initial_args, args)

        if args_diff:
            logger.error(f"Args changed after post-condition!")
            raise DDOIArgumentsChangedException(f"Args changed after pre-condition")
        
        return return_value
    
        # # Check the pre-condition
        # if not cls.pre_condition(args, logger, cfg):
        #     return False

        # # Make sure that the pre-condition did not alter the arguments
        # args_diff = cls._diff_args(args, initial_args)
        # if args_diff:
        #     raise DDOIArgumentsChangedException(
        #         f"Arguments changed after executing pre-condition: {args_diff}")

        # cls.perform(args, logger, cfg)
        # args_diff = cls._diff_args(args, initial_args)
        # if args_diff:
        #     raise DDOIArgumentsChangedException(
        #         f"Arguments changed after executing perform: {args_diff}")

        # pst = cls.post_condition(args, logger, cfg)
        # args_diff = cls._diff_args(args, initial_args)
        # if args_diff:
        #     raise DDOIArgumentsChangedException(
        #         f"Arguments changed after executing post-condition: {args_diff}")
        # return pst

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
        """Compares two flat dictionaries to determine if any values from dict1
        have been changed. Any keys present in dict2 that do not exist in dict1
        are ignored

        Parameters
        ----------
        args1 : dict
            Primary dict to inspect
        args2 : dict
            Secondary dict to inspect

        Returns
        -------
        bool
            True if there is a difference, False otherwise
        """    
        for key in args1.keys():
            if args1[key] != args2[key]:
                return True
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

        config = configparser.ConfigParser(inline_comment_prefixes=(';','#',))
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
    def _add_bool_arg(parser, name, msg, default=False):
        """

        :param parser: <configparser> The parser object.
        :param name: <str> the parameter name
        :param msg: <str> the help message

        :return: <configparser> The parser object.
        """

        def _str_to_bool(arg_val):
            if isinstance(arg_val, bool):
                return arg_val

            if arg_val.lower() in ('yes', 'true', 't', 'y', '1'):
                return True
            elif arg_val.lower() in ('no', 'false', 'f', 'n', '0'):
                return False
            else:
                raise ArgumentTypeError(f'Boolean value expected.')

        parser.add_argument(f'--{name}', type=_str_to_bool, default=default,
                            help=msg)
        return parser

    @classmethod
    def map_OB(cls, OB, sequence_number, cfg=None):
        """Maps values in an OB to a dictionary of arguments to be parsed 
        by the translator module functions. The parameters are loaded in the
        following order, with each subsequent step overwriting any keys with
        conflicting names:

        1. target
        2. acquisition             _
        3. detector parameters      |
        4. instrument parameters    |- from common_parameters
        6. TCS parameters          _|
        7. observation parameters


        Parameters
        ----------
        OB : dict or dictlike
            Observing Block, in dictionary form
        cfg : path or pathlike
            Location of the config file to use to map the OB

        Returns
        -------
        dict
            Dictionary of arguments to be passed into the translator
        """


        # Get the required args into a dictionary
        in_args = {}

        config = cls._load_config(cls, cfg)

        def update_dict(dict_to_update, dic, keys):
            """Searches through the `dic` dictionary using the list of provided
            keys, and updates `dict_to_update` with the found values. If the
            list of keys doesn't have a corresponding value, nothing is added.
             
            to_update = {
                "a" : 1,
                "b" : 2,
                "d" : 4
            }

            OB = {
                'target' :
                    "parameters" :
                        {
                            "a" : 10,
                            "b" : 20,
                            "c" : 30
                        }
            }

            update_dict(to_update, OB, ['target', 'parameters'])
            update_dict(to_update, OB, ['target', 'not_a_key'])

            update_dict:
                {
                    "a" : 10,
                    "b" : 20,
                    "c" : 30,
                    "d" : 4
                }

            Parameters
            ----------
            dict_to_update : dict
                Dictionary that should be updated
            dic : dict
                Dictionary that has the values that should be copied to the
                inputer
            keys : list
                list of keys that lead to the dictionary that contains wanted 
                values
            """
            for key in keys:
                dic = dic.get(key, None)
                if dic == None:
                    # If this key doesn't go anywhere, return the dict unchanged
                    return dict_to_update
            # When we get here, we are at the dict we want to update with
            dict_to_update.update(dic)

        update_dict(in_args, OB, ['target', 'parameters'])
        update_dict(in_args, OB, ['metadata'])
        update_dict(in_args, OB, ['acquisition', 'parameters'])
        update_dict(in_args, OB, ['acquisition', 'metadata'])
        update_dict(in_args, OB, ['common_parameters', 'detector_parameters'])
        update_dict(in_args, OB, ['common_parameters', 'instrument_parameters'])
        update_dict(in_args, OB, ['common_parameters', 'tcs_parameters'])

        # get just this sequence
        for observation in OB['observations']:
            if observation['metadata']['sequence_number'] == sequence_number:
                in_args.update(observation['parameters'])
                in_args.update(observation['metadata'])

        # Map the arguments to their new keys using the config
        out_args = {}

        for key in in_args:
            try:
                newkey = config['ob_keys'][key]
                out_args[newkey] = in_args[key]
            except KeyError:
                out_args[key] = in_args[key]
        return out_args
