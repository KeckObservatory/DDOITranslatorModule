from BaseTranslatorFunction import BaseTranslatorModuleFunction
from DDOIExceptions import *


import numpy as np

ktl = "standin"

class Expose(BaseTranslatorModuleFunction):

    def __init__(self):
        super().__init__()

    def pre_condition(args, logger, cfg):

        return True


    def perform(args, logger, cfg):
        
        return True


    def post_condition(args, logger, cfg):
        logger.debug("No post-condition for expose defined")
        return True
