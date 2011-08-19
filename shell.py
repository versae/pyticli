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
        self.intro = "Pyticli %s by %s.\nLicensed under the terms of %s." \
                     "\nMore info: %s.\n" \
                     % (constants.__version__, constants.__author__,
                        constants.__license__, constants.__url__)
        self.gdb = None

    def do_exit(self, args):
        """Exits from the console"""
        print "May the Force be with you."
        return -1

    def do_EOF(self, args):
        """Exit on system end of file character"""
        return self.do_exit(args)

    def do_help(self, args):
        print self.__doc__

    def do_connect(self, args):
        """Connect to a graph database.
        The first param is the type, althought right now only 'neo4j' through
        REST interface is available.
        The second param es the URL to connect. """
        params = args.strip().split(" ")
        self.type = params[0]
        self.url = params[1]
        if self.type.lower() == "neo4j":
            try:
                from neo4jrestclient import client
                self.gdb = client.GraphDatabase(self.url)
                print u"Connected!"
            except ImportError:
                print u"Depedency not satisfied: neo4jrestclient"
            except:
                print u"Unable to connect to %s database at %s" % (self.type,
                                                                   self.url)
        else:
            print u"Engine %s not supported" % self.type
        print

    def do_disconnect(self, args):
        """Disconnect the graph database"""
        if self.gdb:
            print u"Disconnected %s from %s" % (self.type, self.url)
        else:
            print u"Not previously connected"
        self.gdb = None
        print

    def do_gremlin(self, args):
        """Execute a Gremlin query on a set graph database using 'connect'"""
        if self.gdb:
            self._gremlin_query(args)
        else:
            print u"Graph database not specified"
            print

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
        self._gremlin_query(result)

    def _gremlin_query(self, q):
        if self.gdb:
            if self.type == "neo4j":
                plugin = self.gdb.extensions.GremlinPlugin
                try:
                    print u"Traversal: %s" % plugin.execute_script(script=q)
                except Exception, e:
                    print u"Malformed query: %s" % e
            else:
                print u"Engine %s not supported" % self.type
        print

if __name__ == '__main__':
        ps = PyticliShell()
        ps.cmdloop()
