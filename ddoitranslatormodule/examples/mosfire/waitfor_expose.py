from time import sleep
from datetime import datetime, timedelta
from ddoitranslatormodule import BaseFunction
from ddoitranslatormodule import ddoiexceptions

ktl = "This is just a stand in"

class MOSFIRE_WaitForExpose(BaseFunction.TranslatorModuleFunction):


    def pre_condition(args, logger, cfg):
        logger.info("No precondition")

    def perform(args, logger, cfg):
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
            raise ddoiexceptions.DDOIKTLTimeoutException('Timeout exceeded on waitfor_exposure to finish')
    
    def post_condition(args, logger, cfg):
        logger.info("No postcondition")
