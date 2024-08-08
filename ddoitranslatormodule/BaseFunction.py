from argparse import Namespace, ArgumentTypeError
import configparser
import traceback
import os


class TranslatorModuleFunction:
    """ 
    This is the base class for all Translator Module Functions at Keck.
    """

    @classmethod
    def create_log(logdir='.'):
        self.log = logging.getLogger(f'{self.name}Translator')
        self.log.setLevel(logging.DEBUG)
        ## Set up console output
        LogConsoleHandler = logging.StreamHandler()
        LogConsoleHandler.setLevel(logging.INFO)
        LogFormat = logging.Formatter('%(asctime)s %(levelname)8s: %(message)s')
        LogConsoleHandler.setFormatter(LogFormat)
        self.log.addHandler(LogConsoleHandler)
        ## Set up file output
        logdir = Path(logdir)
        if logdir.exists() is False:
            logdir.mkdir(mode=0o777, parents=True)
        LogFileName = logdir / f'{self.name}Translator_test.log'
        LogFileHandler = RotatingFileHandler(LogFileName,
                                             maxBytes=100*1024*1024, # 100 MB
                                             backupCount=1000) # Keep old files
        LogFileHandler.setLevel(logging.DEBUG)
        LogFileHandler.setFormatter(LogFormat)
        self.log.addHandler(LogFileHandler)
        # Try to change permissions in case they are bad
        try:
            os.chmod(LogFileName, 0o666)
        except OSError as e:
            pass


    @classmethod
    def execute(cls, *args, **kwargs):
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
        cfg = cls._load_config(cls)

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
    def pre_condition(cls, args, kwargs):
      # pre-checks go here
      raise NotImplementedError()

    @classmethod
    def perform(cls, args, kwargs):
        # This is where the bulk of instrument code lives
        raise NotImplementedError()

    @classmethod
    def post_condition(cls, args, kwargs):
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
        config_files = cls._cfg_location(cls)
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
        cfg = f"{cfg_path_base}/{cls.name}_inst_config.ini"
        config_files = [cfg]
        return config_files


    """
    Command line Argument Section for use with CLI (Command Line Interface)
    
        parser = argparse.ArgumentParser()
        args = Function.add_cmdline_args(parser)
        result = Function.execute(args)
    """
    @classmethod
    def add_cmdline_args(cls, parser):
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
