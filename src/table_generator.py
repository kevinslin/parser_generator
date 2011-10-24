#!/usr/bin/env python2.7
"""
LL(1) Table Generator
"""


import argparse
import sys

import compiler


p = argparse.ArgumentParser(description = "parser generator", 
                            formatter_class = argparse.ArgumentDefaultsHelpFormatter)
p.add_argument('-d', '--declarations', nargs = 1, help = "print declarations to stdout")


#class TableGenerator(object):


def main():
    args = p.parse_args(sys.argv[1:])


if __name__ == "__main__":
    r = main()

