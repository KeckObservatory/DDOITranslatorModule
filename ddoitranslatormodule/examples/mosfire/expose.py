from ddoitranslatormodule.BaseFunction import TranslatorModuleFunction

from ddoitranslatormodule.DDOIExceptions import *
import re
from time import sleep

import numpy as np

import ktl

class Expose(TranslatorModuleFunction):

    def __init__(self):
        super().__init__()

    @classmethod
    def pre_condition(cls, args, logger, cfg):
        # Check FCS
        activekw = ktl.cache(keyword='ACTIVE', service='mfcs')
        active = bool(activekw.read())
        if active is not True:
            logger.warn(f'FCS is not active')
            return False
        enabledkw = ktl.cache(keyword='ENABLE', service='mfcs')
        enabled = bool(enabledkw.read())
        if enabled is not True:
            logger.warn(f'FCS is not enabled')
            return False

        return True

    @classmethod
    def perform(cls, args, logger, cfg):
        
        # Set the exposure time
        ITIMEkw = ktl.cache(service='mds', keyword='ITIME')
        new_exptime = float(args.exptime)*1000
        logger.debug(f'Setting exposure time to {new_exptime:.1f} ms')
        ITIMEkw.write(new_exptime)

        # Set coadds
        COADDSkw = ktl.cache(service='mds', keyword='COADDS')
        logger.debug(f'Setting coadds to {int(args.coadds)}')
        COADDSkw.write(int(input))
    
        # Set sampling
        
        namematch = re.match('(M?CDS)(\d*)', input.strip())
        if namematch is None:
            raise DDOIMissingArgumentException(f'Unable to parse "{args.sampmode}"')
        mode = {'CDS': 2, 'MCDS': 3}.get(namematch.group(1))

        SAMPMODEkw = ktl.cache(service='mds', keyword='SAMPMODE')
        NUMREADSkw = ktl.cache(service='mds', keyword='NUMREADS')
        SAMPMODEkw.write(mode)
        if mode == 3:
            nreads = int(namematch.group(2))
            NUMREADSkw.write(nreads)
        
        # Set Object
        objectkw = ktl.cache(service='mds', keyword='OBJECT')
        objectkw.write(args.object)

        # Update FCS

        ROTPPOSNkw = ktl.cache(keyword='ROTPPOSN', service='dcs')
        ROTPPOSN = float(ROTPPOSNkw.read())
        ELkw = ktl.cache(keyword='EL', service='dcs')
        EL = float(ELkw.read())

        FCPA_ELkw = ktl.cache(keyword='PA_EL', service='mfcs')
        FCPA_ELkw.write(f"{ROTPPOSN:.2f} {EL:.2f}")

        FCPA_ELkw = ktl.cache(keyword='PA_EL', service='mfcs')
        FCPA_EL = FCPA_ELkw.read()
        FCSPA = float(FCPA_EL.split()[0])
        FCSEL = float(FCPA_EL.split()[1])
        
        ROTPPOSNkw = ktl.cache(keyword='ROTPPOSN', service='dcs')
        ROTPPOSN = float(ROTPPOSNkw.read())
        ELkw = ktl.cache(keyword='EL', service='dcs')
        EL = float(ELkw.read())
        done = np.isclose(FCSPA, ROTPPOSN, atol=args.PAthreshold)\
            and np.isclose(FCSEL, EL, atol=args.ELthreshold)
        
        if not done:
            logger.warn("Unable to update FCS. Exiting")
            return
        
        # Pad time to ensure proper execution
        sleep(1)

        # Expose!
        GOkw = ktl.cache(service='mds', keyword='GO')
        logger.info('Starting exposure')
        GOkw.write(True)

        return

    @classmethod
    def post_condition(cls, args, logger, cfg):
        logger.debug("No post-condition for expose defined")
        return True
