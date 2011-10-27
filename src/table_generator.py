#!/usr/bin/env python2.7
"""
LL(1) Table Generator
"""


import argparse
import collections
import sys

import compiler
import simplelog


p = argparse.ArgumentParser(description = "parser generator", 
                            formatter_class = argparse.ArgumentDefaultsHelpFormatter)
p.add_argument('-d', '--declarations', nargs = 1, help = "print declarations to stdout")


class TableGenerator(compiler.CompilerBase):
    """
    An LL(1) Table generator)
    """
    def __init__(self, parse_tree):
        """
        Initialze the table generator
        """
        super(TableGenerator, self).__init__()
        self.parse_tree = parse_tree

        #dfs state
        self.IR = collections.defaultdict(list)
        self.FIRST = {}
        self.FOLLOW = {}
        #self.SYMBOL_TABLE = {}

        self.NT = set()
        self.T = set()
        self.SYM = set()
        self.PARENT_STATE = collections.deque()
        self.VISITED = set()
        self.LHS = ""
        self.RHS = []
        

    def initialize(self):
        """
        Determine terminal and non terminal symbols.
        Also convert representation from parse tree 
        into hash table
        """
        self.classify_symbols()
        self.first_set()
        self.follow_set()

    def classify_symbols(self):
        """
        Classify symbols into terminals and non terminals.
        Build up rule table
        """
        self.PARENT_STATE = self._state.GRAMMAR
        self.dfs(self.parse_tree)
        self.T = self.SYM.difference(self.NT)

    def first_set(self):
        """
        Find the first set of given grammar
        """
        for sym in self.T:
            self.FIRST[sym] = set([sym])
        self.FIRST[self.TOKENS.EOF] = set([self.TOKENS.EOF])
        #TODO: epsilon 
        for sym in self.NT:
            self.FIRST[sym] = set()

        CHANGING = True
        while (CHANGING):
            CHANGING = False
            for p in self.IR:
                rhs_old = self.FIRST[p]  #[["baa"], ["sheepnoise"] 
                rhs = set()
                productions = self.IR[p]  #Expr'  -> + Term Expr'
                for expansion in productions:
                    sl.info("expansion: " + str(expansion))
                    first = expansion[0]
                    rhs.update(self.FIRST[first])
                #TODO: account for epsilon
                self.FIRST[p].update(rhs)
                if (rhs_old != rhs): #FIXME: make this more efficient
                    CHANGING = True
        return self.FIRST

    def follow_set(self):
        """
        Find follow set of given grammar
        """
        for sym in self.NT:
            self.FOLLOW[sym] = set()
        #TODO: assume start symbol is goal, is this always the case?
        assert("GOAL" in self.FOLLOW)
        self.FOLLOW["GOAL"].add(self.TOKENS.EOF)

        CHANGING = True
        while (CHANGING):
            CHANGING = False
            #TODO: impose order on these productions
            for p in self.IR:
                trailer = self.FOLLOW(p)
                sl.info("trailer is: " + trailer)
                first = self.FIRST[p]
                productions = self.IR[p]
                for expansion in productions:
                    size = len(expansion)
                    for i in xrange(size, 0, -1):
                        symbol = expansion[i]
                        if (symbol in self.NT):
                            follow_old = self.FOLLOW[symbol]
                            self.FOLLOW(symbol).update(trailer)
                            if (follow_old != self.FOLLOW(symbol)): #FIXME: make more efficient
                                CHANGING = True
                            if (self.TOKENS.EPSILON in self.FIRST[symbol]):
                                trailer.update(self.FIRST[symbol].difference(set([self.TOKENS.EPSILON])))
                            else:
                               trailer.update(self.FIRST[symbol])
                        else:
                            trailer = self.FIRST[symbol]



    #FIXME: obsolete?
    def _first(self, symbol):
        """
        Return a list of symbols
        """
        translation = self.IR[symbol]
        first = []
        for production in translation:
            first.append(production[0])
        return first


    def dfs(self, node):
        """
        Dfs algorithm to explore parse tree.
        Determine terminal & non-terminal symbols
        @param:
        node
        visited
        @return:
        non-termianls - set of non-terminals
        terminals - set of terminal symbols
        ir - intermediate reprsentation 
        """
        #FIXME: this is a hack
        try:
            sl.info("parent state: " + self._state.get_key_for_value(self.PARENT_STATE))
        except IndexError:
            sl.info("parent state: " + self.TOKENS.get_key_for_value(self.PARENT_STATE))
        try:
            sl.info("current state: " + self._state.get_key_for_value(node.type))
        except IndexError:
            sl.info("current state: " + self.TOKENS.get_key_for_value(node.type))
        #check if node has been explored
        if node in self.VISITED:
            return
        self.VISITED.add(node)

        if (self.PARENT_STATE == self._state.PRODUCTIONSET):
            if (node.type == self.TOKENS.SYMBOL):
                sl.info("found lhs: " + node.data)
                self.LHS = node.data
                self.NT.add(node.data)
        else:
            #PS -> SYM : RH
            if (node.type == self.TOKENS.SYMBOL):
                sl.info("found rhs: " + node.data)
                self.SYM.add(node.data)
                self.RHS.append(node.data)
        if(node.type == self._state.PRODUCTIONSET_P):
            sl.info("added new rhs: " + str(self.RHS))
            self.IR[self.LHS].append(self.RHS) 
            self.RHS = []

        for h in node.children:
            self.PARENT_STATE = node.type #maybe better to use stack
            self.dfs(h)


def main():
    args = p.parse_args(sys.argv[1:])


if __name__ == "__main__":
    sl = simplelog.sl
    sl.disable()
    #DEBUG = True
    s = compiler.Scanner("test/RRSheepNoise.txt")
    r = s.execute()
    p = compiler.Parser(r, s.bnf_file)
    r_p = p.execute()
    sl.enable()
    sl.info("========")
    sl.info("========")
    t = TableGenerator(r_p[1])
    r_t = t.initialize()


