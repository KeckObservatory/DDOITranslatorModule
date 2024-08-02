from argparse import Namespace, ArgumentTypeError
import configparser
import traceback


class TranslatorModuleFunction:
    """ 
    This is the base class for all Translator Module Functions at Keck.
    """

    @classmethod
    def execute(cls, args, kwargs, cfg=None):
        """Carries out this function in its entirety (pre and post conditions
           included)

        Parameters
        ----------
        args : dict
            The OB (or portion of OB) in dictionary form
        cfg : filepath, optional
            File path to the config that should be used, by default None
        """
        # read the config file
        cfg = cls._load_config(cls, cfg, args=args)

        #################
        # PRE CONDITION #
        #################
        try:
            cls.pre_condition(args, logger, cfg)
        except Exception as e:
            logger.error(f"Exception encountered in pre-condition: {e}", exc_info=True)
            raise e

        ###########
        # EXECUTE #
        ###########
        try:
            return_value = cls.perform(args, logger, cfg)
        except Exception as e:
            logger.error(f"Exception encountered in perform: {e}", exc_info=True)
            raise e

        ##################
        # POST CONDITION #
        ##################
        try:
            cls.post_condition(args, logger, cfg)
        except Exception as e:
            logger.error(f"Exception encountered in post-condition: {e}")
            logger.error(traceback.format_exc(), exc_info=True)
            raise e

        return return_value

    @classmethod
    def pre_condition(cls, args, kwargs, cfg=cfg):
      # pre-checks go here
      raise NotImplementedError()

    @classmethod
    def perform(cls, args, kwargs, cfg=cfg):
        # This is where the bulk of instrument code lives
        raise NotImplementedError()

    @classmethod
    def post_condition(cls, args, kwargs, cfg=cfg):
        # post-checks go here
        raise NotImplementedError()

    """
    Configuration File Read Section
    """
    def _load_config(cls):
        """
        Load the configuration file for reading

        @param cfg: <str> file path or None
        @param args: <dict> the class arguments

        @return: <class 'configparser.ConfigParser'> the config file parser.
        """
        config_files = self._cfg_location()
        config = configparser.ConfigParser(inline_comment_prefixes=(';','#',))
        config.read(config_files)

        return config

    def _cfg_location(cls):
        """
        Return the fullpath + filename of default configuration file.

        :param args: <dict> The OB (or portion of OB) in dictionary form

        :return: <list> fullpath + filename of default configuration
        """
        cfg_path_base = os.path.dirname(os.path.abspath(__file__))
        cfg = f"{cfg_path_base}/{self.name}_inst_config.ini"
        config_files = [cfg]
        return config_files


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
