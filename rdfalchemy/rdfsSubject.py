#!/usr/bin/env python
# encoding: utf-8
"""
rdfsSubject.py

Created by Philip Cooper on 2008-05-14.
Copyright (c) 2008 Openvest. All rights reserved.
"""

from rdfalchemy import rdfSubject, rdfMultiple, RDF, RDFS
from rdfalchemy.orm import mapper, allsub

_all_ = ['rdfsClass',]

re_ns_n = re.compile(r'(.*[/#])(.*)')

def splitname(uriref):
    return re_ns_n.match(uriref).groups()
    


class rdfsClass(rdfsSubject):
    """rdfSbject with some RDF Schema addons
    *Some* inferencing is implied
    Bleading edge: be careful"""
    rdf_type = RDFS.Class
    subClassOf = rdfMultiple(RDFS.subClassOf, range_type = RDFS.Class)
    
    @property
    def transitive_subClassOf(self):
        return [rdfsClass(s) for s in self.db.transitive_objects(self.resUri,RDFS.subClassOf)]

    @property
    def transitive_subClasses(self):
        return [rdfsClass(s) for s in self.db.transitive_subjects(self.resUri,RDFS.subClassOf)]

    
    def splitname(self):
        re.match(r'(.*[/#])(.*)',self.resUri)
    
    def emit_rdfSubject(self):
        """Procude the text that might be used for a .py file """
        ns,loc = splitname(self.resURI)
        for n in self.subClassOf:
            
        src = "class %s()"
        pass
    
class rdfsSubject(rdfSubject):
    
    @classmethod
    def ClassInstances(cls, beenthere = set([])):
        """return a generator for instances of this rdf:type
        you can look in MyClass.rdf_type to see the predicate being used"""
        # Start with all things of "my" type in the db
        for i in cls.db.subjects(RDF.type, cls.rdf_type):
            if not i in beenthere:
                yield cls(i)
                beenthere.add(i)
        
        # for all subclasses of me in python do the same (recursivly)
        pySubClasses = allsub(cls)
        for sub in pySubClasses:
            for i in sub.ClassInstances():
                if not i in beenthere:
                    yield i 
                    beenthere.add(i)
                    
        # not done yet, for all db subclasses that I have not processed already...get them too
        dbSubClasses = rdfsClass(self.rdf_type).transitive_subClasses
        moreSubClasses = [dbsub.resUri for dbsub in dbSubClasses 
                                if dbsub.resUri not in [pysub.rdf_type for pysub in pySubClasses]
        for sub in moreSubClasses:
            for i in cls.db.subjets(RDF.type, sub):
                if not i in beenthere:
                    yield i
                    beenthere.add(i)        
        
        

    
# this maps the return type of subClassOf back to rdfsClass
mapper(rdfsClass)       

