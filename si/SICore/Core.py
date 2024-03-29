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

class FatalError:
    def __init__(self, message, *args):
        self._message = message.format( args )

    def printMessage(self):
        print self._message

class GitConfig:
    def __init__(self, fileName):
        self._fileName = fileName

    def set(self, key, value):
        return self._run( key, value )

    def get(self, key):
        return self._run( key )

    def getAll(self):
        out = self._run( '-l' )
        kv = {}
        for s in out.split():
            [k, v] = s.split( '=' )
            kv[ k ] = v
        return kv

    def _run(self, *args):
        realArgs = [ 'git', 'config', '-f', self._fileName ]
        for s in args:
            realArgs.append( s )
        return subprocess.check_output( realArgs )

class Config:
    def __init__(self, core, file):
        self._core = core
        self._modules = {}
        self._module = ''
        self._filename = file
        self._gitcfg = GitConfig( file )

        self.parse()

    def parse(self):
        if self._core.debugLevel() > 1:
            print 'Reading .siconf from {0}'.format(self._filename)

        if not os.path.exists( self._filename ):
            # Do we really want this to be printed?
            print '{0} does not exist.'.format( self._filename )
            return

        all = self._gitcfg.getAll()
        for setting in all:
            value = all[ setting ]
            parts = setting.split( '.' )
            if len(parts) == 2:
                subsection = ''
                [ section, key ] = parts
            else:
                [ section, subsection, key ] = parts

            if section == 'core':
                if subsection != '':
                    raise FatalError( 'Bad config option: {}', setting )
                if key == 'standalone':
                    self._standalone = value != '0'

            if section == 'buildsystem':
                if subsection != '':
                    raise FatalError( 'Bad config option: {}', setting )
                if key == 'type':
                    self._buildSystemType = value

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
        raise FatalError( 'Save-Request for {} not implemented, yet', self._name )

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

class BuildSystemUpdater:
    def __init__(self, core, basePath ):
        self._core = core
        self._basePath = basePath

    def update(self):
        pass

class Command:
    def setup(self, core, args):
        self._core = core
        self._args = args
        self._basePath = os.getcwd()
        self._skipBuildSystem = False
        self.parseArguments()

    def addDefaultArguments(self, parser, nobs = False):
        parser.add_argument(
            '-p',
            nargs = '?',
            metavar = 'path',
            help = 'set the base path of the project. Defaults to the current working directory')

        if nobs:
            parser.add_argument(
                '--no-bs',
                default = False,
                action = 'store_true',
                help = 'Do not update the local buildsystem' )

    def handleDefaultArguments(self, opts, nobs = False ):
        if opts.p:
            self._basePath = opts.p
            self._core.setBasePath( opts.p )
        if nobs and opts.no_bs:
            self._skipBuildSystem = opts.no_bs

    def parseArguments(self):
        raise FatalError( 'Command did not supply an argument parser' )

    def updateBuildSystem(self):
        if self._skipBuildSystem:
            return

        bsUpdater = BuildSystemUpdater( self._core, self._basePath )
        bsUpdater.update()

class Subcommand(Command):
    def __init__(self, commandList, defaultCmd, prog, isRoot = False ):
        self._commandList = commandList
        self._defaultCmd = defaultCmd
        self._prog = prog
        self._isRoot = isRoot

    def parseArguments(self):
        parser = argparse.ArgumentParser( prog = self._prog )

        parser.add_argument(
            'cmd',
            nargs = '?',
            choices = self._commandList,
            default = self._defaultCmd )

        if self._isRoot:
            parser.add_argument(
                '-v',
                action = 'count',
                default = 0 )

        parser.add_argument(
            'cmd_opts',
            nargs = argparse.REMAINDER )

        args = parser.parse_args( self._args )

        if self._isRoot:
            self._core._debugLevel = args.v

        self._cmd = self._commandList[ args.cmd ]()
        self._cmd.setup( self._core, args.cmd_opts )
        return self._cmd;

    def run(self):
        self._cmd.run()

class CommandStatus(Command):
    def run(self):
        self._config = self._core.config()
        self._modules = self._core.modules()
        self.showDependencies()

    def parseArguments(self):
        p = argparse.ArgumentParser(
            prog = 'si [status]',
            description = 'Show the status of a local si-project.')

        self.addDefaultArguments( p )
        opts = p.parse_args( self._args )
        self.handleDefaultArguments( opts )

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
            '-u',
            nargs = '?',
            metavar = 'url',
            help = '(Git-)url to checkout, if this is not a standalone project')

        self.addDefaultArguments( p, True )
        opts = p.parse_args( self._args )
        self.handleDefaultArguments( opts, not opts.standalone )

        if opts.standalone:
            self._standalone = True
            self._skipBuildSystem = True
            if opts.u:
                raise FatalError( 'Cannot use url with standalone projects.' )
            self._url = ''
        else:
            self._standalone = False
            if not opts.u:
                raise FatalError( 'Non standalone project requires an url' )
            self._url = opts.u

        self._buildSystem = opts.buildsystem

    def initDirectory(self):
        if os.path.exists( self._basePath ):
            if len( os.listdir( self._basePath ) ) != 0:
                raise FatalError( 'Destination directory {} is not empty'.format( self._basePath ) )
        else:
            os.makedirs( self._basePath )

    def initStandAlone(self):
        self.initDirectory()
        cfg = GitConfig( os.path.join( self._basePath, '.siconf' ) )
        cfg.set( 'core.standalone', '1' )
        cfg.set( 'buildsystem.type', self._buildSystem )

    def initCloned(self):
        self.initDirectory()

    def run(self):
        self.parseArguments()
        if self._standalone:
            self.initStandAlone()
        else:
            self.initCloned()
        self.updateBuildSystem()

class CommandModuleAdd(Command): pass
class CommandModuleList(Command): pass
class CommandModule(Subcommand):
    def __init__(self):
        cmds = {
            'list': lambda: CommandModuleList(),
            'add': lambda: CommandModuleAdd()
        }
        Subcommand.__init__( self, cmds, 'list', 'si module')

class Core:
    def __init__(self):
        self._debugLevel = 0
        self._config = None
        self._basePath = os.getcwd()
        self._modules = None

    def setBasePath(self, basePath):
        if basePath != self._basePath:
            self._config = None
            self._basePath = basePath

    def config(self):
        if self._config == None:
            self._config = Config( self, os.path.join( self._basePath, '.siconf' ) )
        return self._config

    def debugLevel(self):
        return self._debugLevel

    def listCommands(self):
        return {
            'init': lambda: CommandInit(),
            'status': lambda: CommandStatus(),
            'module': lambda: CommandModule()
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
        self._cmd = Subcommand( self.listCommands(),  'status', 'si', True )
        self._cmd.setup( self, sys.argv[ 1: ] )

    def run(self):
        try:
            self.createCommand()
            self._cmd.run()
            if self.debugLevel() > 0:
                print "Success."
        except FatalError as e:
            e.printMessage()
