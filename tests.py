import unittest
import compiler



class TestScanner(unittest.TestCase):
    def setUp(self):
        self.compiler = compiler.Scanner("../RRSheepNoise.txt") #FIXME: use a better test case
        
    def test_get_token(self):
        self.assertTrue(self.compiler.get_token(";") == 0)
        self.assertTrue(self.compiler.get_token(":") == 1)
        self.assertTrue(self.compiler.get_token("|") == 2) 
        self.assertTrue(self.compiler.get_token("EPSILON") == 3)
        self.assertTrue(self.compiler.get_token("boo") == 4)
        return

    def tearDown(self):
        return

class TestParser(unittest.TestCase):
    def setUp(self):
        self.scanner = compiler.Scanner("../RRSheepNoise.txt")
        self.parser = compiler.Parser(self.scanner.execute())

    def test_parser(self):
        return 


    def tearDown(self):
        return

if __name__ == "__main__":
    unittest.main()
