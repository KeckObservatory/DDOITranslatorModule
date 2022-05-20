#! /kroot/rel/default/bin/kpython

import ktl

from ddoitranslatormodule.BaseFunction import TranslatorModuleFunction

class FUNCTION_NAME(TranslatorModuleFunction):
    def __init__(self):
        super().__init__()

    @classmethod
    def pre_condition(cls, args, logger, cfg):
        print("Pre condition")
        return True

    @classmethod
    def perform(cls, args, logger, cfg):
        print("Perform")
        return True
    
    @classmethod
    def post_condition(cls, args, logger, cfg):
        print("Post condition")
        return True