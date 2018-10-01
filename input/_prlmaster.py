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

class PrlMaster(pr.Device):
    def __init__(self,       
            name        = "SysGen",
            description = "System Generator Module",
            **kwargs):
        super().__init__(name=name, description=description, **kwargs)

        self.add(pr.LocalVariable(
            name = 'SysGenType',
            mode = 'RO',
            value = 'PrlMaster',
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
            name        = 'PhaseShift',
            description = 'Additional phase shift',
            offset      = 0x040, 
            mode        = 'RW',
        ))        

        self.add(pr.RemoteVariable(
            name        = 'LoopReset',
            description = 'Loopfilter reset 0 - set, 1 - reset',
            offset      = 0x044, 
            mode        = 'RW',
        ))           

        self.add(pr.RemoteVariable(
            name        = 'LED',
            description = 'Status of LEDs, MSB - blue LED, 2nd bit - red LED, LSB - grn LED.',
            offset      = 0x048, 
            mode        = 'RO',
        ))

        self.add(pr.RemoteVariable(
            name        = 'RawPhiErr',
            description = 'Phase error before the phase shifter',
            offset      = 0x04C, 
            mode        = 'RO',
        ))

        self.add(pr.RemoteVariable(
            name        = 'PhiErrFinal',
            description = 'Phase error after phase shifter',
            offset      = 0x050, 
            mode        = 'RO',
        ))
        
        self.add(pr.RemoteVariable(
            name        = 'LockLogicState',
            description = 'Lock logic state',
            offset      = 0x054, 
            mode        = 'RO',
        ))        
        
        self.add(pr.RemoteVariable(
            name        = 'LoopfilterGain',
            description = 'Last gain block before output',
            offset      = 0x058, 
            mode        = 'RW',
        ))                

        self.add(pr.RemoteVariable(
            name        = 'LoopPolarity',
            description = 'Loopfilter loop 0 - positive, 1 - negative',
            offset      = 0x05C, 
            mode        = 'RW',
        ))                        

        self.add(pr.RemoteVariable(
            name        = 'w1',
            description = 'zero in radian frequency',
            offset      = 0x060, 
            mode        = 'RW',
        ))        

        self.add(pr.RemoteVariable(
            name        = 'w2',
            description = 'pole in radian frequency',
            offset      = 0x064, 
            mode        = 'RW',
        ))                

        self.add(pr.RemoteVariable(
            name        = 'w0',
            description = 'unity gain in radian frequency',
            offset      = 0x068, 
            mode        = 'RW',
        ))          

        self.add(pr.RemoteVariable(
            name        = 'VCO_gain',
            description = 'VCO gain in radian frequency',
            offset      = 0x06C, 
            mode        = 'RW',
        ))          

        self.add(pr.RemoteVariable(
            name        = 'ext_freq_mult',
            description = 'External frequency multiplier gain',
            offset      = 0x070, 
            mode        = 'RW',
        ))          

        self.add(pr.RemoteVariable(
            name        = 'Phase_ramp_gain',
            description = 'phase shift ramp slope',
            offset      = 0x074, 
            mode        = 'RW',
        ))       

        self.add(pr.RemoteVariable(
            name        = 'ADC0_Amp',
            description = 'ADC0 amplitude from CORDIC',
            offset      = 0x078, 
            mode        = 'RO',
        ))       

        self.add(pr.RemoteVariable(
            name        = 'ADC1_Amp',
            description = 'ADC1 amplitude form CORDIC',
            offset      = 0x07C, 
            mode        = 'RO',
        ))  

        self.add(pr.RemoteVariable(
            name        = 'LockDisable',
            description = 'Loop lock disable setting bit in lock logic state machine',
            offset      = 0x080, 
            mode        = 'RW',
        ))          

        self.add(pr.RemoteVariable(
            name        = 'StateReset',
            description = 'Reset the lock logic state machine',
            offset      = 0x084, 
            mode        = 'RW',
        ))          
