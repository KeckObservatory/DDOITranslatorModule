DDOI Translator Modules
=======================

A large part of DDOI is a decoupling of observation planning from instrument
specific code. However, in order to actually run an observation plan at the
observatory, an interface layer needs to exist to translate instrument agnostic
plans into low level (KTL, epics, music, etc) commands on hardware. This module
provides the base code needed to implement that interface layer for any
subsystem.

Installation
------------

Eventually, this package will be provided directly through ``kroot``. However,
until that deployment happens, this package needs to be installed manually.

1. Clone this repo: 
    .. code-block:: bash
        
        git clone https://github.com/KeckObservatory/DDOITranslatorModule.git
2. Install the package:
    .. code-block:: bash

        cd DDOITranslatorModule
        pip install .
3. Check that the installation was successful:
    .. code-block:: bash

        python
        >>> import ddoitranslatormodule

    If no exceptions are raised, the installation was succesful.

Quickstart
----------

What follows is a short example of how to create a single translator module
function. For more information on what specifically should be in a single
function, see the Module Design section (coming soon).

First, import the required pieces from this package

.. code-block:: python
    
    # The base function itself:
    from ddoitranslatormodule.BaseFunction import TranslatorModuleFunction
    # Custom DDOI exceptions:
    from ddoitranslatormodule.DDOIExceptions import *

Next, create a class that extends the ``TranslatorModuleFunction``, and create
the ``__init__`` method:

.. code-block:: python

    class MODULE_NAME_HERE(TranslatorModuleFunction):

        def __init__(self):
            super().__init__()

Finally, add the ``pre_condition``, ``perform``, and ``post_condition`` methods:

.. code-block:: python

    class MODULE_NAME_HERE(TranslatorModuleFunction):

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

Replace the contents of these methods with whatever code makes sense for your
use case. Generally, ``pre_condition`` should only contain code that verifies
that ``perform`` should execute, and ``post_condition`` should contain code that
verifies that the expected change took place. For example, if this module 
function were implementing a filter changing operation, the pre_condition might
check if the system is online, the perform method could command the filter wheel
to rotate, and the post condition could verify that the correct filter is in
place. It does not always makes sense for there to be a pre and post condition, 
if that is the case, then simply ``return True``. 