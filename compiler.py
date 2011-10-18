import collections
import re
import simplelog

from utils import *
from pylibs.data_structures import graph

class CompilerBase(object):
    """
    Base object used by scanner and parser
    Holds the regular expressions
    """
    def __init__(self):
        self.RE = []
        self.DFA = []
        self.DFA_TABLE = [] #tuple object,
        self.TOKENS = Enum("SEMICOLON", "DERIVES", "ALSODERIVES",
                            "EPSILON", "SYMBOL", "EOF")

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

    def _initialize_dfa(self, *args, **kwargs):
        """
        Generate the dfa tables for all given dfa transitions
        """
        self.DFA_TABLE = []

        SEMICOLON_DFA = graph.Graph()
        SEMICOLON_DFA.add_node(0, "NT")
        SEMICOLON_DFA.add_node(1, "T")
        SEMICOLON_DFA.add_edge(0, 1, ";")

        DERIVES_DFA = graph.Graph()
        DERIVES_DFA.add_node(0, "NT")
        DERIVES_DFA.add_node(1, "T")
        DERIVES_DFA.add_edge(0, 1, "|")

        lower_case_letters = "".join(map(chr, xrange(97, 123)))
        upper_case_letters = "".join(map(chr, xrange(65, 91)))
        numbers = "".join(map(chr, xrange(48, 58)))
        alpha_numeric = lower_case_letters + upper_case_letters + numbers
        SYMBOL_DFA = graph.Graph()
        SYMBOL_DFA.add_node(0, "NT")
        SYMBOL_DFA.add_node(1, "T")
        SYMBOL_DFA.add_edge(0, 1, alpha_numeric)
        SYMBOL_DFA.add_edge(1, 1, alpha_numeric)



        self.DFA.append((self.TOKENS.SEMICOLON, SEMICOLON_DFA))
        self.DFA.append((self.TOKENS.DERIVES, DERIVES_DFA))
        self.DFA.append((self.TOKENS.SYMBOL, SYMBOL_DFA))
        
        for name, dfa in self.DFA:
            self.DFA_TABLE.append(self._gen_tables(name, dfa))
        return self.DFA_TABLE

    def _gen_tables(self, name, dfa):
        """
        Generate the dfa tables with given list of DFA's
        @param:
        dfa - the minimized determistic finite automate
        @return:
        tuple consisting of classifier table, transition table, token table
        and set of legal states
        """
        r = bfs(dfa, startnode = 0)
        for key in r[2]:
            r[2][key] = name
        return r
    
    def initialize(self):
        """
        Initialize DFA tables
        """
        self._initialize_re()
        self._initialize_dfa()



        
class Scanner(CompilerBase):
    def __init__(self, filename):
        super(Scanner, self).__init__()
        self.output = []
        self.bnf_file = None
        self.cursor = 0
        self.file_length = 0

        #initialization
        self._get_input(filename)
    
    def _get_input(self, filename):
        """
        Read in the input and get file length
        """
        with open(filename, "rb") as fh:
            self.bnf_file = fh.read()
        self.file_length = len(self.bnf_file)

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

    def next_char(self):
        """
        Get the next character of the input
        and advance cursor position
        """
        #TODO: catch out of bounds error
        out = self._next_char()
        self.cursor += 1
        return out

    def _next_char(self):
        """
        Get the next character of the input
        """
        return self.bnf_file[self.cursor]

    def rollback(self):
        """
        Rollback to earlier character
        """
        #TODO: catch error if cursor goes under 0
        self.cursor -=1

    @simplelog.dump_func()
    def next_word(self):
        """
        Get the enxt word of the input
        @param:
        context - the dfa object, the list
        """
        _STATE = Enum("ERROR", "BAD", start = -2)
        
        #Try every regex to try to get a valid word
        for table_classifier, table_transition, table_token_type, state_legal in \
                self.DFA_TABLE:
            
            state = 0
            lexeme = ""
            stack = collections.deque()
            stack.appendleft(_STATE.BAD)

            while (state != _STATE.ERROR):
                char_curr = self.next_char()
                lexeme += char_curr
                if state in state_legal:
                    stack.clear()
                stack.appendleft(state)
                try:
                    cat = table_classifier[char_curr]
                    state = table_transition[cat][state]
                except KeyError:
                    state = _STATE.ERROR
            
            while ((state not in state_legal) and (state != _STATE.BAD)):
                #roll backed all the way, this isn't the right word
                state = stack.popleft()
                lexeme = lexeme[:-1]
                self.rollback()

                if (lexeme == ""):
                    break
                if state in state_legal:
                    return (lexeme, table_token_type[state])
                #TODO: too much roll back error
        return (False, False)
        
    def execute(self):
        """
        Run scanner
        """
        lino = 1 
        while (self.cursor < self.file_length):
            char = self._next_char()
            #strip white space from input
            if (char == " "):
                self.next_char()
            elif (char == "\n"):
                lino += 1
                self.next_char()
            else:
                import pdb
                pdb.set_trace()
                word, token_type = self.next_word()
                if word is False:
                    #TODO: make a better exception 
                    word = self.bnf_file[self.cursor:self.bnf_file.find(" ")]
                    print (word + " is invalid")
                    raise Exception("Got an invalid character")
                self.output.append({"word":word, "type":token_type, "lino": lino})
        return self.output

        #for lino, line in enumerate(self.bnf_file, start = 1):
            #words = self._split_words(line)
            #for word in words:
                #token = self.get_token(word)
                #self.output.append({"word":word, "token":token, "lino":lino})
                    ##TODO: fail message
        #return self.output

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
    #p = Parser(r)
    #r_p = p.execute()

    

