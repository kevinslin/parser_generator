import compiler
import unittest

import simplelog
from pylibs.data_structures import graph



class TestScanner(unittest.TestCase):
    def setUp(self):
        self.DFA_REG = graph.Graph()
        self.DFA_REG.add_node(0, "NT")
        self.DFA_REG.add_node(1, "NT")
        self.DFA_REG.add_node(2, "T")
        self.DFA_REG.add_edge(0, 1, "r")
        self.DFA_REG.add_edge(1, 2, "0123456789")
        self.DFA_REG.add_edge(2, 2, "0123456789")

        self.compiler = compiler.Scanner("test/reg.txt") #FIXME: use a better test case
        self.compiler.DFA.append(("register", self.DFA_REG))
        self.compiler._initialize_dfa()
    
    @unittest.skip("skip")
    def test_initialize_dfa(self):
        r = self.compiler._initialize_dfa()
        expected_results = ({'1': 1, '0': 1, '3': 1, '2': 1, '5': 1, 
                            '4': 1, '7': 1, '6': 1, '9': 1, '8': 1, 'r': 0}, 
                            {0: {0: 1}, 1: {1: 2, 2: 2}}, 
                            {2: "register"},
                            set([0,1,2]))
        self.assertTrue(r == [expected_results])

    def test_gen_table(self):
        r = self.compiler._gen_tables("register", self.DFA_REG)
        expected_results = ({'1': 1, '0': 1, '3': 1, '2': 1, '5': 1,
                            '4': 1, '7': 1, '6': 1, '9': 1, '8': 1, 'r': 0}, 
                            {0: {0: 1}, 1: {1: 2, 2: 2}}, 
                            {2: "register"},
                            set([0,1,2]))
        self.assertTrue(r == expected_results)
    
    def test_next_word(self):
        r = self.compiler.next_word()
        expected_word = ("r10", "register")
        self.assertTrue(r == expected_word)

    def test_scanner(self):
        r = self.compiler.execute()
        expected_word = [{'lino': 1, 'type': 'register', 'word': 'r10'}]
        self.assertTrue(r == expected_word)

    def test_semicolon(self):
        self.compiler._get_input("test/semicolon.txt")
        self.compiler._initialize_dfa()
        sl.info(self.compiler.DFA_TABLE)
        r = self.compiler.execute()
        print (r)

    def tearDown(self):
        return

@unittest.skip("skipping")
class TestParser(unittest.TestCase):
    def setUp(self):
        self.scanner = compiler.Scanner("../RRSheepNoise.txt")
        self.parser = compiler.Parser(self.scanner.execute())

    def test_parser(self):
        return 


    def tearDown(self):
        return

if __name__ == "__main__":
    sl = simplelog.sl
    unittest.main()
