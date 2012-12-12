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

import os, os.path, string, sys, argparse
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

        if not os.path.exists( self._filename ):
            print '{0} does not exist.'.format( self._filename )
            return

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

    def moduleUrl(self,  moduleName):
        if not moduleName in self._modules:
            return None

        mod = self._modules[ moduleName ]
        if not 'url' in mod:
            return None

        return mod[ 'url' ]

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

    def url(self):
        return self._url

    def setUrl(self, url):
        self._url = url

class Command:
    def setup(self, core, args):
        self._core = core
        self._args = args

class CommandStatus(Command):
    def run(self):
        self._config = self._core.config()
        self._modules = self._core.modules()
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
                
    
class CommandAdd(Command):
    pass

class CommandInit(Command):
    def parseArguments(self):
        p = argparse.ArgumentParser(
            prog = 'si init',
            description = 'Initialize a local si-project.')

        p.add_argument(
            '-s', '--standalone',
            default = False,
            action = 'store_true',
            help = 'create a standalone project' )

        p.add_argument(
            '-b', '--buildsystem',
            default = 'cmake',
            nargs = '?',
            metavar = 'buildsystem', 
            help = 'set the build system used for this project (default: %(default)s)' )

        p.add_argument(
            '-p',
            nargs = '?',
            metavar = 'path',
            help = 'set the base path of the project. Defaults to the current working directory')

        p.add_argument(
            '-u',
            nargs = '?',
            metavar = 'url',
            help = '(Git-)url to checkout, if this is not a standalone project')

        p.add_argument(
            '--no-bs',
            default = False,
            action = 'store_true',
            help = 'Do not update the local buildsystem' )

        opts = p.parse_args( self._args )

        if not opts.p:
            self._path = os.getcwd()
        else:
            self._path = p

        if opts.standalone:
            self._standalone = True
            self._skipBuildSystem = True
            if opts.u:
                print 'Cannot use url with standalone projects.'
                exit(-1)
            self._url = ''
        else:
            self._standalone = False
            self._skipBuildSystem = opts.no_bs
            if not opts.u:
                print 'Non standalone project requires an url'
                exit(-1)
            self._url = opts.u

    def run(self):
        self.parseArguments()
        print self._path,  self._url,  self._standalone,  self._skipBuildSystem

class Core:
    def __init__(self):
        self._debugLevel = 0
        self._config = None
        self._basePath = os.getcwd()
        self._modules = None
        
    def config(self):
        if self._config == None:
            self._config = Config( self, os.path.join( self._basePath, '.siconf' ) )
        return self._config
        
    def debugLevel(self):
        return self._debugLevel

    def listCommands(self):
        return {
            'add': lambda: CommandAdd(),
            'init': lambda: CommandInit(),
            'status': lambda: CommandStatus()
            }

    def buildModules(self):
        self._modules = {}
        cfg = self.config()

        for mod in cfg.modules():
            m = Module( self, mod )
            self._modules[ mod ] = m
            m.setUrl( cfg.moduleUrl( mod ) )

        for mod in cfg.modules():
            deps = cfg.dependencies( mod )
            if deps != None and len(deps):
                modObj = self._modules[ mod ]
                for moddep in deps:
                    if not moddep in self._modules:
                        core.warn( '{} is an unsatisfied dependency of {}' \
                            .format( moddep,  mod ) )
                    else:
                        modObj.addDependency( self._modules[ moddep ] )
                        self._modules[ moddep ].addRequiredBy( modObj )

    def modules(self):
        if self._modules == None:
            self.buildModules()
        return self._modules

    def createCommand(self):
        cmds = self.listCommands()
        
        parser = argparse.ArgumentParser( prog = 'si' )
        parser.add_argument(
            'cmd', nargs='?',
            choices = cmds,
            default ='status' )
        parser.add_argument( '-v', action='count', default=0 )
        parser.add_argument( 'cmd_opts', nargs = argparse.REMAINDER )
        args = parser.parse_args( sys.argv[1:] )

        self._debugLevel = args.v

        command = cmds[ args.cmd ]()
        command.setup(self, args.cmd_opts)
        return command

    def run(self):
        c = self.createCommand()
        c.run()
