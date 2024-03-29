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
        """ 
        Generate the register scanner tables
        """
        r = self.compiler._gen_tables("register", self.DFA_REG)
        expected_results = ({'1': 1, '0': 1, '3': 1, '2': 1, '5': 1,
                            '4': 1, '7': 1, '6': 1, '9': 1, '8': 1, 'r': 0}, 
                            {0: {0: 1}, 1: {1: 2, 2: 2}}, 
                            {2: "register"},
                            set([0,1,2]))
        self.assertTrue(r == expected_results)
   
    @unittest.skip("order matters during checking")
    def test_next_word(self):
        r = self.compiler.next_word()
        expected_word = ("r10", "register")
        print(r)
        self.assertTrue(r == expected_word)

    def test_scanner(self):
        self.compiler._get_input("test/RRSheepNoise.txt")
        r = self.compiler.execute()
        expected = [{'lino': 1, 'type': 4, 'value': 'Goal'}, 
                    {'lino': 1, 'type': 1, 'value': ':'}, 
                    {'lino': 1, 'type': 4, 'value': 'SheepNoise'}, 
                    {'lino': 2, 'type': 0, 'value': ';'}, 
                    {'lino': 3, 'type': 4, 'value': 'SheepNoise'}, 
                    {'lino': 3, 'type': 1, 'value': ':'}, 
                    {'lino': 3, 'type': 4, 'value': 'baa'}, 
                    {'lino': 3, 'type': 4, 'value': 'SheepNoise'}, 
                    {'lino': 4, 'type': 2, 'value': '|'}, 
                    {'lino': 4, 'type': 4, 'value': 'baa'}, 
                    {'lino': 5, 'type': 0, 'value': ';'}, 
                    {'lino': 6, 'type': 5, 'value': ''}]
        self.assertTrue(r == expected)

    def test_semicolon(self):
        self.compiler._get_input("test/semicolon.txt")
        self.compiler._initialize_dfa()
        sl.info(self.compiler.DFA_TABLE)
        r = self.compiler.execute()
        self.assertTrue(r == [{'lino': 1, 'type': 0, 'value': ';'}, 
                                {'lino': 2, 'type': 5, 'value': ''}])

    def test_also_derives(self):
        self.compiler._get_input("test/derives.txt")
        self.compiler._initialize_dfa()
        sl.info(self.compiler.DFA_TABLE)
        r = self.compiler.execute()
        self.assertTrue(r == [{'lino': 1, 'type': 2, 'value': '|'}, 
                                {'lino': 2, 'type': 5, 'value': ''}])

    def test_symbol(self):
        self.compiler._get_input("test/symbol.txt")
        self.compiler._initialize_dfa()
        sl.info(self.compiler.DFA_TABLE)
        r = self.compiler.execute()
        sl.info(r)
        self.assertTrue(r == [{'lino': 1, 'type': 4, 'value': 'foo'}, 
                                {'lino': 2, 'type': 5, 'value': ''}])

    def tearDown(self):
        return

class TestParser(unittest.TestCase):
    def setUp(self):
        self.scanner_sheep = compiler.Scanner("test/RRSheepNoise.txt")
        self.parser_sheep = compiler.Parser(self.scanner_sheep.execute(), 
                                        self.scanner_sheep.bnf_file)
        self.scanner_p = compiler.Scanner("test/P1.txt")
        self.parser_p = compiler.Parser(self.scanner_p.execute(), 
                                        self.scanner_p.bnf_file)

        self.scanner_ceg = compiler.Scanner("test/RRCEG.txt")
        self.parser_ceg = compiler.Parser(self.scanner_ceg.execute(), 
                                        self.scanner_ceg.bnf_file)

    def test_sheep_noise(self):
        r = self.parser_sheep.execute()
        self.assertTrue(r[0] == True)
        #TODO: test the parse tree

    def test_p_noise(self):
        r = self.parser_p.execute()
        self.assertTrue(r[0] == True)

    def test_ceg_noise(self):
        r = self.parser_ceg.execute()
        self.assertTrue(r[0] == True)

    def tearDown(self):
        return

if __name__ == "__main__":
    sl = simplelog.sl
    unittest.main()
