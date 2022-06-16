============================
Creating a Translator Module
============================

Document describes the steps required to create a Translator Module for a
subsystem at Keck. 

Requirements
------------

Requirements for writing the module:
 - An IDE/code editor
 - Python 3.5+
 - Access to the ``ddoitranslatormodule`` python package, which is availible
   through ``kroot`` or via installation from GitHub

Requirements for running the module:
 - KTL Python 3
 - Access to relevant KTL keywords


Getting Started
---------------

Clone the template Translator Module from GitHub at [LINK HERE]

There are three pieces that need to come together for a Translator Module:
 1. The Translator Module functions
 2. setup.py
 3. The other one that I'm forgetting

Translator Module Functions
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Translator Module functions are the meat of a Translator Module. These contain
all of the actual code that executes changes on the observatory, and comprise
the bulk of the work required to build a Translator Module. However, the
overhead on creating each function is low.

Each function file has the same structure:

.. code-block:: python

    from ddoitranslatormodule.BaseFunction import TranslatorModuleFunction

    help = ""

    class MyFunction(TranslatorModuleFunction):

        abortable=False
        min_args = {}

        def __init__(self):
        super().__init__()

        @classmethod
        def pre_condition(cls, args, logger, cfg):
            pass
        
        @classmethod
        def perform(cls, args, logger, cfg):
            pass

        @classmethod
        def post_condition(cls, args, logger, cfg):
            pass

        @classmethod
        def abort_execution(cls, args, logger, cfg):
            pass