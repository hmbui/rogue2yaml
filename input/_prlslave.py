#!/usr/bin/env python
#-----------------------------------------------------------------------------
# Title      : PyRogue _sysgen Module
#-----------------------------------------------------------------------------
# File       : _sysgen.py
# Author     : Larry Ruckman <ruckman@slac.stanford.edu>
# Created    : 2016-11-09
# Last update: 2016-11-09
#-----------------------------------------------------------------------------
# Description:
# PyRogue _sysgen Module
#-----------------------------------------------------------------------------
# This file is part of the LCLS2-PRL. It is subject to 
# the license terms in the LICENSE.txt file found in the top-level directory 
# of this distribution and at: 
#    https://confluence.slac.stanford.edu/display/ppareg/LICENSE.html. 
# No part of the LCLS2-PRL, including this file, may be 
# copied, modified, propagated, or distributed except according to the terms 
# contained in the LICENSE.txt file.
#-----------------------------------------------------------------------------

import pyrogue as pr

class PrlSlave(pr.Device):
    def __init__(self,       
            name        = "SysGen",
            description = "System Generator Module",
            **kwargs):
        super().__init__(name=name, description=description, **kwargs)

        self.add(pr.LocalVariable(
            name = 'SysGenType',
            mode = 'RO',
            value = 'PrlSlave',
        ))

        self.add(pr.RemoteVariable(
            name        = 'Version',
            description = 'User version number',
            offset      = 0x000, 
            mode        = 'RO',
        ))   

        self.add(pr.RemoteVariable(
            name        = 'ScratchPad',
            description = 'User scratchpad',
            offset      = 0xFFC, 
            mode        = 'RW',
        ))