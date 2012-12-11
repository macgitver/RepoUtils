#
# Source-Integration scripts
# (C) 2012 Sascha Cunz
# sascha@babbelbox.org
#
# This program is free software. It comes without any warranty, to
# the extent permitted by applicable law. You can redistribute it
# and/or modify it under the terms of the Do What The Fuck You Want
# To Public License, Version 2, as published by Sam Hocevar. See
# http://sam.zoy.org/wtfpl/COPYING for more details.

import subprocess

class Config:
    def __init__(self, core, file):
        self._core = core
        self._modules = {}
        self._module = ''
        self._filename = file
        
        self.parse()
        
    def parse(self):
        if self._core.debugLevel() > 1:
            print 'Reading .siconf from {0}'.format(self._filename)

        out = subprocess.check_output( [ 'git', 'config',  '-f',  self._filename, '-l' ] )
        for s in out.split():
            [setting, value] = s.split( '=' )
            parts = setting.split( '.' )
            if len(parts) == 2:
                subsection = ''
                [ section, key ] = parts
            else:
                [ section, subsection, key ] = parts
            if section == 'modules':
                if not subsection in self._modules:
                    self._modules[subsection] = {};
                if key == 'url':
                    self._modules[subsection]['url'] = value
                elif key == 'depends':
                    if not 'depends' in self._modules[subsection]:
                        self._modules[subsection]['depends'] = [];
                    self._modules[subsection]['depends'].append( value )

    def modules(self):
        for key in self._modules:
            yield key
    
    def dependencies(self, moduleName ):
        if not moduleName in self._modules:
            return None
        
        mod = self._modules[ moduleName ]        
        if not 'depends' in mod:
            return None
        
        return mod[ 'depends' ]
