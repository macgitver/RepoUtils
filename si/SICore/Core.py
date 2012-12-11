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

import SICore.Commands
from SICore.Config import Config

class Core:
    def __init__(self):
        self._debugLevel = 0
        self._config = None
        self._basePath = os.getcwd()
        
    def config(self):
        if self._config == None:
            self._config = Config( self, os.path.join( self._basePath, '.siconf' ) )
        return self._config
        
    def debugLevel(self):
        return self._debugLevel

    def run(self):
        c = self.createCommand()
        c.run()
    
    def createCommand(self):
        parser = argparse.ArgumentParser( prog = 'si' )
        parser.add_argument( \
            'cmd', nargs='?', \
            choices= SICore.Commands.listCommands(), \
            default='status' )
        parser.add_argument( '-v', action='count', default=0 )
        parser.add_argument( 'cmd_opts',  nargs='*' )
        args = parser.parse_args( sys.argv[1:] )
        exec "command = SICore.Commands.{0}()".format(string.capitalize(args.cmd))
        self._debugLevel = args.v
        command.setup(self, args.cmd_opts)
        return command
