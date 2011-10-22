import collections
import re
import simplelog

from utils import *
from pylibs.data_structures import graph, tree

class CompilerBase(object):
    """
    Base object used by scanner and parser
    Holds the regular expressions
    """
    def __init__(self):
        self.RE = []
        self.DFA = []
        self.DFA_TABLE = [] #tuple object (token type, token dfa) 
        self.TOKENS = Enum("SEMICOLON", "DERIVES", "ALSODERIVES",
                            "EPSILON", "SYMBOL", "EOF")

    def _initialize_re(self, *args, **kwargs):
        """
        Initialize regular expressions
        """
        #TODO: remove this 
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

    @simplelog.dump_func(func_name_only = True)
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
        DERIVES_DFA.add_edge(0, 1, ":")

        ALSODERIVES_DFA = graph.Graph()
        ALSODERIVES_DFA.add_node(0, "NT")
        ALSODERIVES_DFA.add_node(1, "T")
        ALSODERIVES_DFA.add_edge(0, 1, "|")

        EPSILON_DFA = graph.Graph()
        EPSILON_DFA.add_node(0, "NT") 
        EPSILON_DFA.add_node(1, "NT") #E
        EPSILON_DFA.add_node(2, "NT") #P
        EPSILON_DFA.add_node(3, "NT") #S
        EPSILON_DFA.add_node(4, "NT") #I
        EPSILON_DFA.add_node(5, "NT") #L
        EPSILON_DFA.add_node(6, "NT") #O
        EPSILON_DFA.add_node(7, "T") #N

        EPSILON_DFA.add_node(8, "NT")
        EPSILON_DFA.add_node(9, "NT")
        EPSILON_DFA.add_node(10, "NT")
        EPSILON_DFA.add_node(11, "NT")
        EPSILON_DFA.add_node(12, "NT")
        EPSILON_DFA.add_node(13, "NT")
        EPSILON_DFA.add_node(14, "T")

        EPSILON_DFA.add_edge(0, 1, "E")
        EPSILON_DFA.add_edge(1, 2, "P")
        EPSILON_DFA.add_edge(2, 3, "S")
        EPSILON_DFA.add_edge(3, 4, "I")
        EPSILON_DFA.add_edge(4, 5, "L")
        EPSILON_DFA.add_edge(5, 6, "O")
        EPSILON_DFA.add_edge(6, 7, "N")

        EPSILON_DFA.add_edge(0, 8, "e")
        EPSILON_DFA.add_edge(8, 9, "p")
        EPSILON_DFA.add_edge(9, 10, "s")
        EPSILON_DFA.add_edge(10, 11, "i")
        EPSILON_DFA.add_edge(11, 12, "l")
        EPSILON_DFA.add_edge(12, 13, "o")
        EPSILON_DFA.add_edge(13, 14, "n")

        EPSILON_DFA.add_edge(1, 9, "p") #Episilon

        lower_case_letters = "".join(map(chr, xrange(97, 123)))
        upper_case_letters = "".join(map(chr, xrange(65, 91)))
        numbers = "".join(map(chr, xrange(48, 58)))
        alpha_numeric = lower_case_letters + upper_case_letters + numbers
        SYMBOL_DFA = graph.Graph()
        SYMBOL_DFA.add_node(0, "NT")
        SYMBOL_DFA.add_node(1, "T")
        SYMBOL_DFA.add_edge(0, 1, alpha_numeric)
        SYMBOL_DFA.add_edge(1, 1, alpha_numeric)
        
        #Order matters when adding the DFA 
        self.DFA.append((self.TOKENS.SEMICOLON, SEMICOLON_DFA))
        self.DFA.append((self.TOKENS.DERIVES, DERIVES_DFA))
        self.DFA.append((self.TOKENS.ALSODERIVES, ALSODERIVES_DFA))
        self.DFA.append((self.TOKENS.EPSILON, EPSILON_DFA))
        self.DFA.append((self.TOKENS.SYMBOL, SYMBOL_DFA))
        
        #Generate tables for everyone
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
    @simplelog.dump_func(func_name_only = True)
    def __init__(self, filename):
        """
        Scanner that takes a Back Naur Form (BNF) input
        file and tokenizes it 
        """
        super(Scanner, self).__init__()
        self.output = []
        self.bnf_file = None
        self.cursor = 0
        self.file_length = 0

        #initialization
        self._get_input(filename)
        self.initialize()
    
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
        context - the dfa object, the 
        @return
        tuple object (value, state) 
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
                #TODO: too much roll back error?
        return (False, False)
    
    @simplelog.dump_func()
    def execute(self):
        """
        Run scanner and words into tokens
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
                word, token_type = self.next_word()
                if word is False:
                    #TODO: make a better exception 
                    word = self.bnf_file[self.cursor:self.bnf_file.find(" ")]
                    print (word + " is invalid")
                    raise Exception("Got an invalid character")
                self.output.append({"value":word, "type":token_type, "lino": lino})
        self.output.append({"value":"", "type":self.TOKENS.EOF, "lino": lino})
        return self.output

class Parser(CompilerBase):
    def __init__(self, input_scan, input_raw):
        """
        Parser for bnf langauge
        Build a parse tree for language
        """
        super(Parser, self).__init__()
        self.input_raw = input_raw
        self.input_scan = input_scan 
        self.index = 0
        self.word = "" 

        self._state = Enum("GRAMMAR", "PRODUCTIONLIST", "PRODUCTIONSET",
                            "RIGHTHANDSIDE", "SYMBOLLIST", start = 6)
        self._expected_state = []
        self.ast = collections.deque() #abstract syntax tree
        self.output = []

    @simplelog.dump_func()
    def next_word(self):
        """
        get next word
        """
        word = self.input_scan[self.index]
        self.index += 1
        self.word = word
        return self.word #FIXME: this is only for debugging

    @simplelog.dump_func()
    def is_grammar(self):
        """
        Checks if word is goal
        Grammer -> ProductionList
        """
        self._expected_state.append(self._state.GRAMMAR) #log current expected state 
        self.next_word()
        if (self.is_production_list()):
            if(self.word["type"] == self.TOKENS.EOF):
                self._expected_state.pop()
                return True
        self.fail()

    @simplelog.dump_func()
    def is_production_list(self):
        """
        Check if a word is a production list
        ProductionList -> ProductionSet SEMICOLON ProductionList'
        """
        self._expected_state.append(self._state.PRODUCTIONLIST)
        if self.is_production_set():
            if self.is_production_list_p():
                self._expected_state.pop()
                return True
        self.fail()

    @simplelog.dump_func()
    def is_production_list_p(self):
        """
        ProductionList' -> ProductionSet SEMICOLON ProductionSet'
                        | EPSILON
        """
        import pdb
        pdb.set_trace()
        if (self.is_epsilon()):
            return True
        else:
            #we reached end of a productionlist; move forward to next set
            self.next_word()  
            if self.is_production_set():
                import pdb
                pdb.set_trace()
                if (self.word['type'] == self.TOKENS.SEMICOLON):
                    node = tree.Node(";", self.TOKENS.SEMICOLON)
                    for child in self.ast:
                        node.add_child(child)
                    self.next_word()
                    if (self.is_production_list_p()):
                        return True
        self.fail()

    @simplelog.dump_func()
    def is_production_set(self):
        """
        Check if word is a production set
        ProductionSet -> SYMBOL DERIVES RightHandSide PS'
        """
        self._expected_state.append(self._state.PRODUCTIONSET)
        if (self.word["type"] == self.TOKENS.SYMBOL):
            self.next_word()
            if (self.word["type"] == self.TOKENS.DERIVES):
                self.next_word()
                node = tree.Node(":", self.TOKENS.DERIVES)
                if (self.is_right_hand_side()):
                    if (self.is_production_set_p()):
                        self._expected_state.pop()
                        return True
        self.fail()

    @simplelog.dump_func()
    def is_production_set_p(self):
        """
        ProductionSet' -> ALSODERIVES PS'
                        | EPSILON
        """
        if(self.is_epsilon()):
            return True
        elif (self.word["type"] == self.TOKENS.ALSODERIVES):
            self.next_word()
            if (self.is_right_hand_side()):
                if(self.is_production_set_p()):
                    return True
        self.fail()

    @simplelog.dump_func()
    def is_right_hand_side(self):
        """
        Check if word is a valid right hand side
        RH -> Symbolist 
            | Epsilon
        """
        self._expected_state.append(self._state.RIGHTHANDSIDE)
        if (self.is_symbol_list()):
            self._expected_state.pop()
            return True
        elif (self.word["type"] == self.TOKENS.EPSILON):
            self._expected_state.pop()
            return True
        self.fail()

    
    @simplelog.dump_func()
    def is_symbol_list(self):
        """
        Check if word is valid symbolist
        SL ->  SYMBOL SL'
        """
        self._expected_state.append(self._state.SYMBOLLIST)
        if (self.word["type"] == self.TOKENS.SYMBOL):
            self.next_word()
            if (self.is_symbol_list_p()):
                self._expected_state.pop()
                return True
        self.fail()
    
    @simplelog.dump_func()
    def is_symbol_list_p(self):
        """
        Perform followng Check:
        SL' -> SYMBOL SL'
            | EPSILON
        """
        if self.is_epsilon():
            return True
        elif (self.word["type"] == self.TOKENS.SYMBOL):
            self.next_word()
            if (self.is_symbol_list_p()):
                return True
        self.fail()

    def is_epsilon(self):
        """
        Check if word is epsilon
        """
        if (self.word["type"] == self.TOKENS.EPSILON):
            return True
        elif (self.expected_state == self._state.SYMBOLLIST):
            if ( 
                (self.word["type"] == self.TOKENS.SEMICOLON) | 
                (self.word["type"] == self.TOKENS.ALSODERIVES)
               ):
                return True
        elif (self.expected_state == self._state.PRODUCTIONSET):
            if (self.word["type"] == self.TOKENS.SEMICOLON):
                return True
        elif (self.expected_state == self._state.PRODUCTIONLIST):
            if (self.word["type"] == self.TOKENS.EOF):
                return True
        return False

    @simplelog.dump_func()
    def fail(self):
        """
        Dump out information regarding failure
        """
        import pdb
        pdb.set_trace()
        print ("failure")
        error_msg = ""
        word = self.word
        error_msg += "error!\n"
        error_msg += "expected: " + str(self.expected_state) + "\n"
        error_msg += "got: " + str(word["type"]) + "\n"
        error_msg += "line number: " + str(word["lino"]) + "\n"
        error_msg += "word: " + word['word'] + "\n"
        print (error_msg) 
        print (self.input_raw)
        from pprint import pprint
        pprint(self.input_scan)
        pprint(self.input_raw)
        #TODO: attempt recovery
        exit()

    @simplelog.dump_func()
    def execute(self):
        """
        Run parser
        """
        if self.is_grammar():
            return True
        else:
            self.fail()

    @property
    def expected_state(self):
        """
        The expected state of the program
        """
        #TODO: account for case of empty list
        try:
            return self._expected_state[-1]
        except IndexError:
            return []


                


if __name__ == "__main__":
    sl = simplelog.sl
    sl.quiet()
    sl.debug("=========")
    sl.debug("new trial")
    s = Scanner("test/RRSheepNoise.txt")
    r = s.execute()
    p = Parser(r, s.bnf_file)
    r_p = p.execute()

    

