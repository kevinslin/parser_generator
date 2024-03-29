import collections
import numpy
import sys

class Enum(dict):
    """
    C enum substitute
    """
    #TODO: get key for value
    def __init__(self, *args, **kwargs):
        """
        Initialize with default start value of 0 but this can be changed
        with keyword argument start
        @param:
        start - set starting element
        verbose - display values by value instead of number
        """
        super(Enum, self).__init__()
        self.verbose = None

        if kwargs.has_key("start"):
            start = kwargs["start"]
        else:
            start = 0
        
        if kwargs.has_key("verbose"):
            self.verbose = kwargs["verbose"]

        for num, arg in enumerate(args, start):
            self.__setitem__(arg, num)

    def __getattr__(self, name):
        """
        Return attribute if it exists in the dictionary
        """
        if self.__contains__(name):
            if (self.verbose):
                return self.get_key_for_key(name)
            return self.__getitem__(name)

    def get_key_for_key(self, key):
        """
        Return key given key
        """
        if (key in self):
            return key
        else:
            raise KeyError("invalid key")

    def get_key_for_value(self, value):
        """
        Get key for value
        >>> t = Enum("A", "B", "C")
        >>> t.get_key_for_value(1)
        'B'
        >>> t.verbose = True
        >>> t.A
        'A'
        """
        if (self.verbose):
            return self.get_key_for_key(value)
        else:
            return filter(lambda x: x[1] == value, self.items())[0][0]
    
def bfs(g, startnode, **kwargs):
    """
    Implement bfs algo. Explore graph in first in first out fashion.
    @params
    g is an undirected graph
    starnode is the starting node
    numnodes is the number of unique nodes to explore
    @return
    classifier table - maps a string to a transition class
    transition table - creates a matrix of transition and states
    token tyle table - maps valid return tokens depending on current state
    visited_states - the acceptable states for regex
    """
    #initialization
    table_classifier = dict()
    table_transition = collections.defaultdict(dict)
    table_token_type = dict()
    visited_transitions = set()

    Q = collections.deque([]) #nodes in the query
    W = set() #nodes that have been processed
    Q.append(startnode)

    acc_transition = 0
    while (len(Q)>0) :
        state = Q.popleft() # FIFO policy
        neighbors = g[state]
        for h in neighbors:
            if h in W: #don't process nodes in W, not unique
                continue
            transition = g.get_edge_attr(state, h)
            #got a new transition
            if transition not in visited_transitions:
                visited_transitions.add(transition)
                for t in transition:
                    table_classifier[t] =  acc_transition 
                acc_transition += 1
            transition_class = table_classifier[transition[0]] #only want one char
            #add new valid state to transition table
            table_transition[transition_class][state] = h
            #check if we have a valid terminal state
            if (g.get_node_attr(h) == "T"):
                table_token_type[h] = True
            Q.append(h)
        W.add(state)
    return table_classifier, table_transition, table_token_type, W





"""
A better dictionary
"""


class SimpleDict(collections.defaultdict):
    def __init__(self, *args, **kwargs):
        try:
            self.__root
        except AttributeError:
            self.__root = root = []
            root[:] = [root, root, None]
            self.__map = {}
        super(SimpleDict, self).__init__(*args, **kwargs)


    def __setitem(self, key, value, PREV=0, NEXT=1, dict_setitem=dict.__setitem__):
        if key not in self:
            root = self.__root
            last = root[PREV]
            last[NEXT] = root[PREV] = self.__map[key] = [last, root, key]
        dict_setitem(self, key, value)
        super(SimpleDict, self).__setitem(self, key, value, PREV=0, NEXT=1, dict_setitem=dict.__setitem__)

    def __iter__(self):
        NEXT, KEY = 1, 2
        root = self.__root
        curr = root[NEXT]
        while curr is not root:
            yield curr[KEY]
            curr = curr[NEXT]


    def keys(self):
        return list(self)

if __name__ == "__main__":
    import doctest
    doctest.testmod()
