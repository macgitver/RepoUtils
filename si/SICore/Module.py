
import SICore.Config

class Module:
    def __init__(self, core, name):
        self._core = core
        self._name = name
        self._dependsOn = {}
        self._requiredBy = {}

    def store(self):
        print 'Save-Request for {} not implemented, yet' \
            .format(self._name)

    def dependsOn(self):
        return self._dependsOn
        
    def requiredBy(self):
        return self._requiredBy
        
    def name(self):
        return self._name
        
    def addDependency(self, moduleObj):
        if not moduleObj in self._dependsOn:
            self._dependsOn[ moduleObj.name() ] = moduleObj
        
    def addRequiredBy(self, moduleObj):
        if not moduleObj in self._requiredBy:
            self._requiredBy[ moduleObj.name() ] = moduleObj

def buildModules(core):
    modules = {}
    cfg = core.config()

    for mod in cfg.modules():
        modules[ mod ] = Module( core,  mod )

    for mod in cfg.modules():
        deps = cfg.dependencies( mod )
        if deps != None and len(deps):
            modObj = modules[ mod ]
            for moddep in deps:
                if not moddep in modules:
                    core.warn( '{} is an unsatisfied dependency of {}' \
                        .format( moddep,  mod ) )
                else:
                    modObj.addDependency( modules[ moddep ] )
                    modules[ moddep ].addRequiredBy( modObj )

    return modules
    
