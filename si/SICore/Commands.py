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

import string

import SICore.Module

class Command:
    def setup(self, si, args):
        self._core = si
        self._args = args

class Status(Command):
    def run(self):
        self._config = self._core.config()
        self._modules = SICore.Module.buildModules(self._core)
        self.showDependencies()
    
    def showDependencies(self):
        for name in self._modules:
            m = self._modules[ name ]
            deps = m.dependsOn()
            requ = m.requiredBy()
            if len(deps) + len(requ) > 0:
                print name
                if len(deps) > 0:
                    print "\tDepends on  :",  string.join( m.dependsOn(),  '; ' )
                if len(requ) > 0:
                    print "\tRequired by :",  string.join( m.requiredBy(),  '; ' )
                print "\tURL         :",  m.url()
            else:
                print name, '(Not required)'
                
    
class Add(Command):
    pass

class Init(Command):
    def run(self):
        pass

def listCommands():
    return [\
        'add',
        'init',
        'status'
        ]
