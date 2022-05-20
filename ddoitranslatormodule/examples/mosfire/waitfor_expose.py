#! /kroot/rel/default/bin/kpython

from time import sleep
from datetime import datetime, timedelta
from ddoitranslatormodule.BaseFunction import TranslatorModuleFunction
from ddoitranslatormodule.DDOIExceptions import *

import ktl

class MOSFIRE_WaitForExpose(TranslatorModuleFunction):

    @classmethod
    def pre_condition(cls, args, logger, cfg):
        logger.info("No precondition")

    @classmethod
    def perform(cls, args, logger, cfg):
        timeout = cfg['waitfor_expose']['timeout']
        endat = datetime.utcnow() + timedelta(seconds=timeout)
        logger.debug(f"Timeout is set to {timeout} seconds, timeout at {endat}")
        sleep(1)
        IMAGEDONEkw = ktl.cache(service='mds', keyword='IMAGEDONE')
        READYkw = ktl.cache(service='mds', keyword='READY')

        imagedone = bool(int(IMAGEDONEkw.read()))
        mdsready = bool(int(READYkw.read()))
        done_and_ready = imagedone and mdsready
        while datetime.utcnow() < endat and not done_and_ready:
            sleep(0.5)
            imagedone = bool(int(IMAGEDONEkw.read()))
            mdsready = bool(int(READYkw.read()))
            done_and_ready = imagedone and mdsready
        if not done_and_ready:
            raise DDOIKTLTimeoutException('Timeout exceeded on waitfor_exposure to finish')
    
    @classmethod
    def post_condition(cls, args, logger, cfg):
        logger.info("No postcondition")
