import collections

class Enum(dict):
    """
    C enum substitute
    """
    #TODO: get key for value
    def __init__(self, *args):
        super(Enum, self).__init__()
        for num, arg in enumerate(args):
            self.__setitem__(arg, num)

    def __getattr__(self, name):
        """
        Return attribute if it exists in the dictionary
        """
        if self.__contains__(name):
            return self.__getitem__(name)
    

        


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
