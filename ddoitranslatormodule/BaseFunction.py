from ddoitranslatormodule.ddoiexceptions.DDOIExceptions import DDOIArgumentsChangedException
from logging import getLogger

from deepdiff import DeepDiff

class TranslatorModuleFunction():
    """ 
    This is the base class for all Translator Module Functions at Keck.
    """
    
    # If True, then the abort_execution method may be invoked
    abortable = False

    @classmethod
    def execute(cls, args, logger=None, cfg=None):

        # Access the logger and pass it into each method
        if logger is None:
            logger = getLogger("")
        # if cfg is None:
        #     cfg = cls._load_config("")
        # Store a copy of the initial args
        initial_args = args.copy()
        print(f"Executing {__name__}")
        
        # Check the pre-condition
        if cls.pre_condition(args, logger, cfg):
        # Make sure that the pre-condition did not alter the arguments
            args_diff = cls._diff_args(args, initial_args)
            if args_diff is not None:
                raise DDOIArgumentsChangedException(f"helpful message {args_diff}")
            
            cls.perform(args, logger, cfg)
            args_diff = cls._diff_args(args, initial_args)
            if args_diff is not None:
                raise DDOIArgumentsChangedException(f"helpful message {args_diff}")
            
            pst = cls.post_condition(args, logger, cfg)
            args_diff = cls._diff_args(args, initial_args)
            if args_diff is not None:
                raise DDOIArgumentsChangedException(f"helpful message {args_diff}")
            return pst
        return False
        
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
        if cfg is None:
            cfg = cls._load_config("")

        if cls.abortable:
            cls.abort_execution(args, logger, cfg)
        else:
            logger.error("Failed to abort. abort_execution() is not enabled")
        # Code for shutting everything down, even while perform is operating
        raise NotImplementedError()
    
    def _diff_args(args1, args2):

        return DeepDiff(args1, args2)
    
    def _load_config():
        return

    def copy(arg):
        print()