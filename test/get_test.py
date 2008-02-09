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


def test_addBNodeKnowsL():
    Person.knows = rdflibList(FOAF.knowsL, range_type=FOAF.Person)        
    p1=Person(first="PhilipL")
    p2=Person(last="Cooper" , first="Ben")
    p3=Person(last="Cooper" , first="Matt")
    p1.knows = [p2, p3]
    p1=Person.get_by(first="PhilipL")
    log.info("db len is %s"%len(Person.db))
    assert len(p1.knows) == 2
    del p1
    
def test_addBNodeKnowsC():
    Person.knows = rdflibContainer(FOAF.knowsC, range_type=FOAF.Person)        
    p1=Person(first="PhilipC")
    p2=Person(last="Cooper" , first="Ben")
    p3=Person(last="Cooper" , first="Matt")
    p1.knows = [p2, p3]
    p1=Person.get_by(first="PhilipC")
    log.info("db len is %s"%len(Person.db))
    assert len(p1.knows) == 2
    del p1
    
def test_addBNodeKnowsM():
    Person.knows = rdflibMultiple(FOAF.knowsM, range_type=FOAF.Person)        
    p1=Person(first="PhilipM")
    p2=Person(last="Cooper" , first="Ben")
    p3=Person(last="Cooper" , first="Matt")
    p1.knows = [p2, p3]
    p1=Person.get_by(first="PhilipM")
    log.info("db len is %s"%len(Person.db))
    assert len(p1.knows) == 2
    del p1
    
    

