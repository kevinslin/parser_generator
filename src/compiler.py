import collections
import re
import simplelog

from utils import *
from pylibs.data_structures import graph, tree

class CompilerBase(object):
    """
    Base object used by scanner and parser.
    """
    def __init__(self):
        """
        Initialize the compiler
        @param:
        debug - if true, print verbose output in Enum data types,
                looks for a global DEBUG variable. 
        """
        self.DFA = []
        self.DFA_TABLE = [] #tuple object (token type, token dfa) 
        self.debug = False
        if globals().has_key("DEBUG"):
            self.debug = globals()["DEBUG"]
        #TODO: make eof something that can't appear in the grammar 
        self.TOKENS = Enum("SEMICOLON", "DERIVES", "ALSODERIVES",
                            "EPSILON", "SYMBOL", "EOF",
                            verbose = self.debug)
        self._state = Enum("GRAMMAR", "PRODUCTIONLIST", "PRODUCTIONSET",
                            "RIGHTHANDSIDE", "SYMBOLLIST", "SYMBOLLIST_P",
                            "PRODUCTIONSET_P", "PRODUCTIONLIST_P", start = 6, 
                            verbose = self.debug)

class Scanner(CompilerBase):
    """
    Scanner for BNF grammar
    """
    @simplelog.dump_func(func_name_only = True)
    def __init__(self, filename):
        """
        Scanner that takes a Back Naur Form (BNF) input
        file and tokenizes it 
        @param:
        filename - input file with bnf text
        """
        super(Scanner, self).__init__()
        self.output = []
        self.bnf_file = None
        self.cursor = 0
        self.file_length = 0

        #initialization
        self._get_input(filename)
        self.initialize()
    
    def initialize(self):
        """
        Initialize the dfa tables
        """
        self._initialize_dfa()

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

    
    def _get_input(self, filename):
        """
        Read in the input and get file length
        """
        with open(filename, "rb") as fh:
            self.bnf_file = fh.read()
        self.file_length = len(self.bnf_file)

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
            
            state = 0 #start state
            lexeme = ""
            stack = collections.deque()
            stack.appendleft(_STATE.BAD)

            while (state != _STATE.ERROR) and (self.cursor < self.file_length):
                char_curr = self.next_char()
                lexeme += char_curr
                if state in state_legal:
                    stack.clear()
                stack.appendleft(state)
                try:
                    cat = table_classifier[char_curr] #look up category
                    state = table_transition[cat][state] #look up if we reached a valid state
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
                #if state is not here, we got an invalid entry 
                try:
                    return (lexeme, table_token_type[state])
                except KeyError:
                    continue
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
            elif (char == "\t"):
                self.next_char()
            else:
                word, token_type = self.next_word()
                if word is False:
                    #TODO: make a better exception 
                    word = self.bnf_file[self.cursor:self.bnf_file.find(" ")]
                    print (word + " is invalid")
                    print ("cursor position: " + str(self.cursor))
                    print ("lino: " + str(lino))
                    raise Exception("Got an invalid character")
                self.output.append({"value":word, "type":token_type, "lino": lino})
        self.output.append({"value":"", "type":self.TOKENS.EOF, "lino": lino})
        return self.output

class Parser(CompilerBase):
    """
    Parser for bnf grammar. Uses a recursive descent parser
    """
    def __init__(self, input_scan, input_raw):
        """
        Parser for bnf langauge
        Build a parse tree for language
        @parser:
        input_scan - tokenized output of scanner
        input_raw - input text of bnf file 
        """
        super(Parser, self).__init__()
        self.input_raw = input_raw
        self.input_scan = input_scan 
        self.index = 0
        self.word = "" 

        self._type = Enum("NT", "T", "UNKNOWN", verbose = self.debug)
        self._expected_state = []
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
        valid, result= self.is_production_list()
        if (valid):
            self.ast = result 
            if(self.word["type"] == self.TOKENS.EOF):
                self._expected_state.pop()
                return True
        return self.fail()

    @simplelog.dump_func()
    def is_production_list(self):
        """
        Check if a word is a production list
        ProductionList -> ProductionSet SEMICOLON ProductionList'
        """
        pl_node = tree.Node("", self._state.PRODUCTIONLIST)
        self._expected_state.append(self._state.PRODUCTIONLIST)

        valid, result = self.is_production_set()
        if (valid):
            pl_node.add_child(result)
            if (self.word["type"] == self.TOKENS.SEMICOLON):
                pl_node.add_child(tree.Node(";", self.TOKENS.SEMICOLON))
                self.next_word()
                valid, result = self.is_production_list_p()
                if (valid):
                    pl_node.add_child(result)
                    self._expected_state.pop()
                    return (True, pl_node)
        return self.fail()

    @simplelog.dump_func()
    def is_production_list_p(self):
        """
        ProductionList' -> ProductionSet SEMICOLON ProductionSet'
                        | EPSILON
        """
        plp_node = tree.Node("", self._state.PRODUCTIONLIST_P)
        valid, result = self.is_epsilon()
        if (valid):
            plp_node.add_child(result)
            return (True, plp_node)
        else:
            valid, result = self.is_production_set()
            if (valid):
                plp_node.add_child(result)
                if (self.word['type'] == self.TOKENS.SEMICOLON):
                    plp_node.add_child(tree.Node(";", self.TOKENS.SEMICOLON))
                    self.next_word()
                    valid, result = self.is_production_list_p()
                    if (valid):
                        plp_node.add_child(result)
                        return (True, plp_node)
        return self.fail()

    @simplelog.dump_func()
    def is_production_set(self):
        """
        Check if word is a production set
        ProductionSet -> SYMBOL DERIVES RightHandSide PS'
        """
        ps_node = tree.Node("", self._state.PRODUCTIONSET)
        self._expected_state.append(self._state.PRODUCTIONSET)

        if (self.word["type"] == self.TOKENS.SYMBOL):
            ps_node.add_child(tree.Node(self.word["value"],self.TOKENS.SYMBOL)) 
            self.next_word()
            if (self.word["type"] == self.TOKENS.DERIVES):
                ps_node.add_child(tree.Node(":", self.TOKENS.DERIVES))
                self.next_word()
                valid, result = self.is_right_hand_side()
                if (valid):
                    ps_node.add_child(result)
                    valid, result = self.is_production_set_p()
                    if (valid):
                        ps_node.add_child(result)
                        self._expected_state.pop()
                        return (True, ps_node)
        return self.fail()

    @simplelog.dump_func()
    def is_production_set_p(self):
        """
        ProductionSet' -> ALSODERIVES PS'
                        | EPSILON
        """
        psp_node = tree.Node("", self._state.PRODUCTIONSET_P)
        self._expected_state.append(self._state.PRODUCTIONSET_P)

        valid, result = self.is_epsilon()
        if(valid):
            psp_node.add_child(result)
            self._expected_state.pop()
            return (True, psp_node)
        elif (self.word["type"] == self.TOKENS.ALSODERIVES):
            psp_node.add_child(tree.Node("|", self.TOKENS.ALSODERIVES))
            self.next_word()
            valid, result = self.is_right_hand_side()
            if (valid):
                psp_node.add_child(result)
                valid, result = self.is_production_set_p()
                if(valid):
                    psp_node.add_child(result)
                    self._expected_state.pop()
                    return (True, psp_node)
        return self.fail()

    @simplelog.dump_func()
    def is_right_hand_side(self):
        """
        Check if word is a valid right hand side
        RH -> Symbolist 
            | Epsilon
        """
        rh_node = tree.Node("", self._state.RIGHTHANDSIDE)
        self._expected_state.append(self._state.RIGHTHANDSIDE)

        valid, result = self.is_epsilon()
        if(valid):
            rh_node.add_child(result)
            self.next_word() #epsilon consumes input in right hand side
            self._expected_state.pop()
            return (True, rh_node)
        valid, result = self.is_symbol_list()
        if (valid) or (self.word["type"] == self.TOKENS.EPSILON):
            rh_node.add_child(result)
            self._expected_state.pop()
            return (True, rh_node)
        return self.fail()

    
    @simplelog.dump_func()
    def is_symbol_list(self):
        """
        Check if word is valid symbolist
        SL ->  SYMBOL SL'
        """
        sl_node = tree.Node("", self._state.SYMBOLLIST)
        self._expected_state.append(self._state.SYMBOLLIST)
        if (self.word["type"] == self.TOKENS.SYMBOL):
            sl_node.add_child(tree.Node(self.word["value"], self.TOKENS.SYMBOL))
            self.next_word()
            valid, result = self.is_symbol_list_p()
            if (valid):
                sl_node.add_child(result)
                self._expected_state.pop()
                return (True, sl_node)
        return self.fail()
    
    @simplelog.dump_func()
    def is_symbol_list_p(self):
        """
        Perform followng Check:
        SL' -> SYMBOL SL'
            | EPSILON
        """
        slp_node = tree.Node("", self._state.SYMBOLLIST_P)
        valid, result = self.is_epsilon()
        if (valid):
            slp_node.add_child(result)
            return (True, slp_node)
        elif (self.word["type"] == self.TOKENS.SYMBOL):
            slp_node.add_child(tree.Node(self.word["value"],
                                self.TOKENS.SYMBOL)) 
            self.next_word()
            valid, result = self.is_symbol_list_p()
            if (valid):
                slp_node.add_child(result)
                return (True, slp_node)
        return self.fail()

    def is_epsilon(self):
        """
        Check if word is epsilon
        """
        #ASSUME: RHS has to be a epsilon production
        empty_node = tree.Node("", "")
        if (self.expected_state == self._state.RHS):
            assert (self.word["type"] == self.TOKENS.EPSILON)
        if (self.word["type"] == self.TOKENS.EPSILON):
            import pdb
            pdb.set_trace()
            epsilon = tree.Node("EPSILON", self.TOKENS.EPSILON)
            return (True, epsilon)
        elif (self.expected_state == self._state.SYMBOLLIST):
            if ( 
                (self.word["type"] == self.TOKENS.SEMICOLON) | 
                (self.word["type"] == self.TOKENS.ALSODERIVES)
               ):
                return (True, empty_node)
        elif (
                (self.expected_state == self._state.PRODUCTIONSET) |
                (self.expected_state == self._state.PRODUCTIONSET_P)
             ):
            if (self.word["type"] == self.TOKENS.SEMICOLON):
                return (True, empty_node)
        elif (self.expected_state == self._state.PRODUCTIONLIST):
            if (self.word["type"] == self.TOKENS.EOF):
                return (True, empty_node)
        return (False, empty_node)

    @simplelog.dump_func()
    def fail(self):
        """
        Dump out information regarding failure
        """
        import pdb
        pdb.set_trace()
        error_msg = ""
        word = self.word
        error_msg += "error!\n"
        error_msg += "expected: " + str(self._state.get_key_for_value(self.expected_state)) +\
                     "\n"
        error_msg += "got: " + str(self.TOKENS.get_key_for_value(word["type"])) + "\n"
        error_msg += "line number: " + str(word["lino"]) + "\n"
        error_msg += "word: " + word['value'] + "\n"
        print (error_msg) 
        print (self.input_raw)
        from pprint import pprint
        #pprint(self.input_scan)
        pprint(self.input_raw)
        exit()
        #TODO: attempt recovery
        return False

    @simplelog.dump_func()
    def execute(self):
        """
        Run parser
        """
        if self.is_grammar():
            return (True, self.ast)
        else:
            return self.fail()

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
    DEBUG = True
    sl = simplelog.sl
    sl.quiet()
    sl.debug("=========")
    sl.debug("new trial")

    #s = Scanner("test/RRSheepNoise.txt")
    #r = s.execute()
    #p = Parser(r, s.bnf_file)
    #r_p = p.execute()
    #print(r_p)
    #r_p[1].dump()

    s = Scanner("test/RRCEG.txt")
    r = s.execute()
    p = Parser(r, s.bnf_file)
    r_p = p.execute()
    print(r_p)
    r_p[1].dump()




