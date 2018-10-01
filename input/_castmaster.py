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

class CastMaster(pr.Device):
    def __init__(self,       
            name        = "SysGen",
            description = "System Generator Module",
            **kwargs):
        super().__init__(name=name, description=description, **kwargs)

        self.add(pr.LocalVariable(
            name = 'SysGenType',
            mode = 'RO',
            value = 'CastMaster',
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

        self.add(pr.RemoteVariable(
            name        = 'DAC2route',
            description = 'DAC2 route mux: 0 - 0, 1 - ADC2, 2 - ADC3',
            offset      = 0x010, 
            mode        = 'RW',
        ))   

        self.add(pr.RemoteVariable(
            name        = 'DAC3route',
            description = 'DAC3 route mux: 0 - 0, 1 - ADC2, 2 - ADC3',
            offset      = 0x014, 
            mode        = 'RW',
        ))                  

        self.add(pr.RemoteVariable(
            name        = 'Amp0',
            description = 'ADC0 Amplitude',
            offset      = 0x018, 
            mode        = 'RO',
        ))          

        self.add(pr.RemoteVariable(
            name        = 'Amp1',
            description = 'ADC1 Amplitude',
            offset      = 0x01C, 
            mode        = 'RO',
        ))          

        self.add(pr.RemoteVariable(
            name        = 'Amp_status',
            description = 'Amplitude status, 1 - both channel 25% < ampl < 89%',
            offset      = 0x020, 
            mode        = 'RO',
        ))                  

        self.add(pr.RemoteVariable(
            name        = 'LED',
            description = 'Status of LEDs, MSB - blue LED, 2nd bit - red LED, LSB - grn LED.',
            offset      = 0x024, 
            mode        = 'RO',
        ))              