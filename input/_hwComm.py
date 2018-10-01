#!/usr/bin/env python
#-----------------------------------------------------------------------------
# Title      : PyRogue _hwComm Module
#-----------------------------------------------------------------------------
# File       : _hwComm.py
# Author     : Larry Ruckman <ruckman@slac.stanford.edu>
# Created    : 2016-11-09
# Last update: 2016-11-09
#-----------------------------------------------------------------------------
# Description:
# PyRogue _hwComm Module
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

class HwComm(pr.Device):
    def __init__(self,       
            name        = "HwComm",
            description = "Hardware-to-Hardware Communication Module",
            **kwargs):        
        super().__init__(name=name, description=description, **kwargs)

        
        def addPair(name,offset,description):
            for i in range(2):
                rawName = ('%sRaw[%d]' % (name,i))
                self.add(pr.RemoteVariable(  
                    name         = rawName, 
                    description  = description,
                    offset       = (offset + i*0x10), 
                    bitSize      = 32, 
                    bitOffset    = 0,
                    base         = pr.UInt, 
                    mode         = 'RO', 
                    pollInterval = 1,
                    hidden       = True,
                ))
                self.add(pr.LinkVariable(
                    name         = ('%s[%d]' % (name,i)), 
                    mode         = 'RO', 
                    units        = 'Hz',
                    linkedGet    = self.convtFreq,
                    disp         = '{:1.0f}',
                    dependencies = [self.variables[rawName]],
                )) 
                
        addPair(
            name        = 'TxFrameRate', 
            description = '',
            offset      = 0x00,         
        )
        
        addPair(
            name        = 'TxFrameRateMax', 
            description = '',
            offset      = 0x04,         
        )    

        addPair(
            name        = 'TxFrameRateMin', 
            description = '',
            offset      = 0x08,         
        )            
        
        self.addRemoteVariables( 
            name        = 'TxBackPressureCnt', 
            description = '',
            offset      = 0x0C, 
            bitSize     = 32, 
            bitOffset   = 0, 
            base        = pr.UInt,
            mode        = 'RO',
            number      = 2,
            stride      = 0x10,  
            pollInterval = 1,
        )
        
        addPair(
            name        = 'RxFrameRate', 
            description = '',
            offset      = 0x20,         
        )
        
        addPair(
            name        = 'RxFrameRateMax', 
            description = '',
            offset      = 0x24,         
        )    

        addPair(
            name        = 'RxFrameRateMin', 
            description = '',
            offset      = 0x28,         
        )            
        
        self.addRemoteVariables( 
            name        = 'RxErrDropCnt', 
            description = '',
            offset      = 0x2C, 
            bitSize     = 32, 
            bitOffset   = 0, 
            base        = pr.UInt,
            mode        = 'RO',
            number      = 2,
            stride      = 0x10,
            pollInterval = 1,            
        )        
        
        self.add(pr.RemoteVariable(
            name        = 'TxEnable', 
            description = '',
            offset      = 0x80, 
            bitSize     = 2, 
            bitOffset   = 0, 
            base        = pr.UInt,
            mode        = 'RW',
        )) 

        self.add(pr.RemoteVariable(  
            name        = 'TxRateRaw', 
            description = '',
            offset      = 0x84, 
            mode        = 'RW',
            hidden      = True,
        ))
        
        self.add(pr.LinkVariable(
            name         = 'TxRate', 
            mode         = 'RW', 
            units        = 'Hz',
            linkedGet    = self.getTxRate,
            linkedSet    = self.setTxRate,
            dependencies = [self.variables['TxRateRaw']],
        ))         
        
        self.add(pr.RemoteVariable(
            name        = 'HwDacSel', 
            description = '',
            offset      = 0x8C, 
            bitSize     = 2, 
            bitOffset   = 0, 
            base        = pr.UInt,
            mode        = 'RW',
        ))                 
        
    def countReset(self):
        self._rawWrite(0x88,1)

    @staticmethod
    def getTxRate(var):
        value = var.dependencies[0].value()
        return int((100.0E+6)/(value+1.0))

    @staticmethod
    def setTxRate(var, value, write):
        # Check for a non-negative value
        if (value>0):
            # Calculate the RAW value
            newValue = ((100.0E+6)/(value))-1.0
            # Update the register
            var.dependencies[0].set(int(newValue),write)
        else:
            print( 'HwComm.setTxRate(): %d Hz is an invalue TX rate setting' % value )
        
    @staticmethod
    def convtFreq(var):
        return (var.dependencies[0].value())
                                    
