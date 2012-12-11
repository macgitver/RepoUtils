#!/usr/bin/python


import subprocess
import argparse
import sys
import os

#from SICore.Core import CoreX
import SICore.Core

os.chdir( '/work/mgv2/src' )
si = SICore.Core.Core()
si.run()

#main()


#class cmd_status:
#    def run(self):
#        self.siconf = SiConf('.siconf')
#
#class cmd_add:
#    def run(self):
#        print "cmd add"
#        
#def createCommand():
#    global debuglevel
#
#    parser = argparse.ArgumentParser( prog = 'si' )
#    parser.add_argument( \
#        'cmd', nargs='?', \
#        choices=['status', 'add', 'remove'], \
#        default='status' )
#    parser.add_argument( '-v', action='count', default=0 )
#    parser.add_argument( 'cmd_opts',  nargs='*' )
#    args = parser.parse_args( sys.argv[1:] )
#    exec "command = cmd_" + args.cmd + "()"
#    debuglevel = args.v
#    return command
#
#def main():
#    c = createCommand()
#    c.run()
