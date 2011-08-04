#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Based on http://www.juanjoconti.com.ar/2007/11/02/minilisp-un-ejemplo-de-ply/
import cmd

from pyticli import Program, constants


class PyticliShell(cmd.Cmd):
    """
    Pyticli Shell allows the input of ITL propositions to
    translate them to graph database query language.

    You can type formulae like:
    :> next(always(I==3) and next(next(J==4))) and next(J==1)
    
    :> next(always(I==1 and next(I<5))) and next(next(next(J==2)))
       and next(J==3 or I==J+H) and I<4 or next(R<=5)
    
    :> next(I >= J)
    """

    def __init__(self):
        cmd.Cmd.__init__(self)
        self.prompt = ":> "
        self.intro = "Pyticli %s by %s.\nLicensed under the terms of %s" \
                     "\nMore info: %s.\n" \
                     % (constants.__version__, constants.__author__,
                        constants.__license__, constants.__url__)

    def do_exit(self, args):
        """Exits from the console"""
        return -1

    def do_EOF(self, args):
        """Exit on system end of file character"""
        print "May the Force be with you"
        return self.do_exit(args)

    def do_help(self, args):
        print self.__doc__

    def emptyline(self):
        """Do nothing on empty input line"""
        pass

    def default(self, line):
        """Called on an input line when the command prefix
           is not recognized.
           In that case we execute the line as Python code.
        """
        result = None
        try:
            result = Program(line).query(verbose=1)
        except Exception, e:
            result = e
        print result
        print

if __name__ == '__main__':
        ps = PyticliShell()
        ps.cmdloop()
