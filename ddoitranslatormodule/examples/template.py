from ddoitranslatormodule import BaseFunction
from ddoitranslatormodule import ddoiexceptions

ktl = "standin"

class FUNCITON_NAME(BaseFunction.TranslatorModuleFunction):

    def __init__(self):
        super().__init__()

    def pre_condition(args, logger, cfg):

        return True


    def perform(args, logger, cfg):
        
        return True


    def post_condition(args, logger, cfg):
        logger.debug("No post-condition for expose defined")
        return True
