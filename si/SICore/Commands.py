
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
                    print "\tDepends on:",  string.join( m.dependsOn(),  '; ' )
                if len(requ) > 0:
                    print "\tRequired by:",  string.join( m.requiredBy(),  '; ' )
            else:
                print name, '(Not required)'
                
    
class Add(Command):
    pass
