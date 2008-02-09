from rdfalchemy import *
from rdfalchemy.samples.doap import *
from rdfalchemy.samples.foaf import *
from rdflib import ConjunctiveGraph

import logging
log = logging.getLogger('rdfalchemy')
if not log.handlers:
    log.addHandler(logging.StreamHandler())
#log.setLevel(10)


Person.db=ConjunctiveGraph()

def test_start():
    assert len(Person.db) == 0
    p=Person(last="Cooper")
    assert len(Person.db) == 2



Person.m=rdfMultiple(FOAF.multi)
Person.l=rdfList(FOAF.list)
Person.c=rdfContainer(FOAF.seq)

def test_multi():
    p=Person.ClassInstances().next()
    p.m = [1,2.2,0,'a','','c']
    assert len(Person.db) == 8
    
    p.m = ['a','b','c']
    assert len(Person.db) == 5

def test_list():
    # set and reset a list
    p=Person.ClassInstances().next()
    p.l = [10,2.3,0,'A','','C']
    assert len(Person.db) == 18
    
    p.l = [10,2.3,0]
    assert len(Person.db) == 12

def test_seq():
    p=Person.ClassInstances().next()
    p.c = range(10)
    assert len(Person.db) == 24
    
    p.c = ['things', 44]
    assert len(Person.db) == 16


