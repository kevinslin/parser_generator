import collections
import re

from utils import *
import simplelog
import simplecache

class CompilerBase(object):
    """
    Base object used by scanner and parser
    Holds the regular expressions
    """
    def __init__(self):
        self.RE = []

    def _initialize_re(self, *args, **kwargs):
        """
        Initialize regular expressions
        """
        self.RE.append({'name' : 'RE_SEMICOLON',
                        'pattern' : re.compile(";"),
                        'token' : 0})
        self.RE.append({'name' : 'RE_DERIVES',
                        'token' : 1,
                        'pattern' : re.compile(":")})
        self.RE.append({'name':'RE_ALSODERIVES',
                        'token' : 2, 
                        'pattern' : re.compile("\|")})
        self.RE.append({'name':'RE_EPSILON',
                        'pattern' : re.compile("EPSILON|epsilon|Epsilon"),
                        'token' : 3})
        self.RE.append({'name' : 'RE_SYMBOL',
                        'pattern' : re.compile("[a-zA-Z0-9]+"),
                        'token' : 4})
        self.RE.append({'name':'RE_EOF',
                        'pattern' : re.compile(""),
                        'token' : 5})

class Scanner(CompilerBase):
    def __init__(self, filename):
        super(Scanner, self).__init__()
        self.output = []
        self.bnf_file = None
        self.input_split = None #input split into words
        self.cursor_pos = 0

        #initialization
        self._initialize_re()
        self._get_input(filename)
        self._split_words()
        return
    
    def _get_input(self, filename):
        """
        Read in the input 
        """
        with open(filename, "rb") as fh:
            self.bnf_file = fh.read()

    def _split_words(self):
        """
        Split input into words
        """
        self.input_split = re.split("\s+", self.bnf_file)
    
    def get_token(self, word):
        """
        Given a word, get the token for it
        """
        for re in self.RE:
            if re['pattern'].match(word):
                return re['token']
        
    def execute(self):
        """
        Run scanner
        """
        for word in self.input_split:
            token = self.get_token(word)
            if (token):
                self.output.append({"word":word, "token":token})
        return self.output

class Parser(CompilerBase):
    def __init__(self, input_scan):
        super(Parser, self).__init__()

        self.input_scan = input_scan 
        self.input_pos = 0
        self.token = Enum("SEMICOLON", "DERIVES", "ALSODERIVES",
                            "EPSILON", "SYMBOL", "EOF")
        self.symbol_table = None

        self.output = []
        self.state = {}

        #initialization
        self._initialize_re()

    def next_word(self):
        """
        get next word
        """
        word = self.input_scan[self.input_pos]
        self.input_pos += 1
        return word

    def is_grammar(self, word):
        """
        Checks if word is goal
        """
        print("checking if word is a grammar")
        if word == self.token.SYMBOL:
            word = self.next_word()
            if word == self.token.DERIVES:
                word = self.next_word()



    def execute(self):
        """
        Run parser
        """
        word = self.next_word()
        if self.is_grammar(word):
            word = self.next_word()
            sl.debug("found a grammar")
            if (word['token'] == self.token.EOF):
                return True
            else:
                print ("could not parse")
                return False


                


if __name__ == "__main__":
    sl = simplelog.sl
    s = Scanner("../RRSheepNoise.txt")
    r = s.execute()
    p = Parser(r)

    

