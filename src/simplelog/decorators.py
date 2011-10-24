"""
This module holds decorators used for simplelog.
"""

import functools
import sys

__all__ = ["dump_func"]

def dump_func(level = None, func_name_only = False, pretty = True):
    """
    This decorate captures the input values of a particular function
    @param:
    level - debug level
    """
    #TODO: make the level actually do something useful
    #TODO: don't return result in func_name_only
    def decorator(function):
        @functools.wraps(function) #propagate docstring to children 
        def wrapper(*args, **kwargs):

            log = ""
            func_name = function.__name__
            log += "function: " + func_name + "\n"
            if not func_name_only:
                log += "args: "
                log += ", ".join(["{0!r}".format(a) for a in args]) 
                log += "\n"
                log += "kwargs: " 
                log += ", ".join(["{0!r}".format(a) for a in kwargs]) 
                log += "\n"
            result = exception = None

            #get result or error
            try:
                result = function(*args, **kwargs)
            except Exception as err:
                exception = err
            finally: 
                if exception is None:
                    log += ("result: " + str(result))
                else:
                    import traceback
                    log += ("exception: {0}:{1}".format(type(exception),
                                exception))
                    log += ("{0}".format(traceback.format_exc()))

                if pretty:
                    log += "\n==============\n"

                #Log message
                try:
                    if level:
                        print ("level is " + level)
                    sl = globals()['sl']
                    sl.debug(log)
                except KeyError:
                    import simplelog
                    sl = simplelog.sl
                    sl.quiet()
                    sl.debug(log)
                    pass
                finally:    
                    if exception: #FIXME: put somewhere better
                        raise exception
                    return result
        return wrapper
    return decorator


