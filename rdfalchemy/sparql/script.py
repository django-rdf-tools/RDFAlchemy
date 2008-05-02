#!/usr/bin/env python
# encoding: utf-8
"""
script.py

Created by Philip Cooper on 2008-04-29.
Copyright (c) 2008 Openvest. 
BSD License.
"""
from rdfalchemy.sparql import SPARQLGraph

import sys
import re
import getopt


help_message = '''
The help message goes here.
'''


class Usage(Exception):
    def __init__(self, msg):
        self.msg = msg


def main(url=None):
    
    try:
        output = ""
        
        try:
            opts, args = getopt.getopt(sys.argv[1:], "hu:o:t:v", ["help", "output=","url=", "format="])
        except getopt.error, msg:
            raise Usage(msg)
            
    
        # option processing
        for option, value in opts:
            if option == "-v":
                verbose = True
            if option in ("-h", "--help"):
                raise Usage(help_message)
            if option in ("-o", "--output"):
                output = value
            if option in ("-t","--format"):
                resultMethod = value
            if option in ("-u", "--url"):
                url = value

        if len(args) > 1:
            Usage("you must give at most one filename.")
        fname = len(args) and args[-1] or '-'
        
        if fname == '-':
            stream = sys.stdin
        else:
            stream = file(fname)
            
        query = stream.read()
        
        if not output:
            output = sys.stdout
        else:
            output = open(output)
        
        if not url:
            try:
                url =  re.search(r'(?:^|\n) *# *--url=([^ \s\n]+)',query).groups()[0]
            except:
                raise ValueError, "Need a url for the endpoint"

        result = SPARQLGraph(url).query(query,resultMethod = "xml",rawResults=True)
        print >>output, result.read()

            
    
    except Usage, err:
        print >> sys.stderr, sys.argv[0].split("/")[-1] + ": " + str(err.msg)
        print >> sys.stderr, "\t for help use --help"
        return 2


if __name__ == "__main__":
    sys.exit(main())
