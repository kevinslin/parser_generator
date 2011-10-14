import collections
import re
import simplelog

from utils import *

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
        self.cursor_pos = 0

        #initialization
        self._initialize_re()
        self._get_input(filename)
    
    def _get_input(self, filename):
        """
        Read in the input 
        """
        with open(filename, "rb") as fh:
            self.bnf_file = fh.readlines()

    def _split_words(self, line):
        """
        Split input into words
        @param:
        line - given line of text
        """
        words = re.split("\s+", line)
        return words
    
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
        for lino, line in enumerate(self.bnf_file, start = 1):
            words = self._split_words(line)
            for word in words:
                token = self.get_token(word)
                self.output.append({"word":word, "token":token, "lino":lino})
                    #TODO: fail message
        return self.output

class Parser(CompilerBase):
    def __init__(self, input_scan):
        super(Parser, self).__init__()

        self.input_scan = input_scan 
        self.input_pos = 0
        self.token = Enum("SEMICOLON", "DERIVES", "ALSODERIVES",
                            "EPSILON", "SYMBOL", "EOF")
        self._state = Enum("GRAMMAR", "PRODUCTIONLIST", "PRODUCTIONSET",
                            "RIGHTHANDSIDE", "SYMBOLLIST")
        self.state = -1

        self.output = []

        #initialization
        self._initialize_re()

    def next_word(self):
        """
        get next word
        """
        word = self.input_scan[self.input_pos]
        self.input_pos += 1
        return word

    @simplelog.dump_func()
    def is_grammar(self, word):
        """
        Checks if word is goal
        """
        self.state = self._state.GRAMMAR
        if (word['token'] == self.token.SYMBOL):
            word = self.next_word()
            if (word['token'] == self.token.DERIVES):
                word = self.next_word()
                if self.is_production_list(word):
                    word = self.next_word()
                    if (word['token'] == self.token.EOF):
                        print ("successful parse")
                        return True
        else:
            self.fail()
            return False

    @simplelog.dump_func()
    def is_production_list(self, word):
        """
        Check if a word is a production list
        """
        self.state = self._state.PRODUCTIONLIST
        if self.is_production_set(word):
            word = self.next_word()
            if (word['token'] == self.token.SEMICOLON):
                return True
        else:
            self.fail()
            return False

    @simplelog.dump_func()
    def is_production_set(self, word):
        """
        Check if word is a production set
        """
        return False

    def fail(self):
        """
        Dump out information regarding failure
        """
        print ("failure")
        error_msg = ""
        word = self.input_scan[self.input_pos]
        error_msg += "error!\n"
        error_msg += "current state: " + str(self.state) + "\n"
        error_msg += "line number: " + str(word["lino"]) + "\n"
        error_msg += "word: " + word['word'] + "\n"
        print (error_msg) 
        from pprint import pprint
        pprint(self.input_scan)
        return False

    @simplelog.dump_func()
    def execute(self):
        """
        Run parser
        """
        word = self.next_word()
        if self.is_grammar(word):
            word = self.next_word()
            if (word['token'] == self.token.EOF):
                return True
            else:
                print ("could not parse")
                return False


                


if __name__ == "__main__":
    sl = simplelog.sl
    sl.quiet()
    sl.debug("=========")
    sl.debug("new trial")
    s = Scanner("../RRSheepNoise.txt")
    r = s.execute()
    p = Parser(r)
    r_p = p.execute()

    

