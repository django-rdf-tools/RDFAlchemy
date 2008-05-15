#!/usr/bin/env python
# encoding: utf-8
"""
rdfsSubject.py

Created by Philip Cooper on 2008-05-14.
Copyright (c) 2008 Openvest. All rights reserved.
"""

from rdfalchemy import rdfSubject, rdfSingle, rdfMultiple, RDF, RDFS, Namespace
from rdfalchemy.orm import mapper, allsub
import re

OWL = Namespace("http://www.w3.org/2002/07/owl#")

_all_ = ['rdfsSubject','rdfsClass','rdfsProperty',
         'owlObjectProperty','owlDatatypeProperty',
         'owlFunctionalProperty','owlInverseFunctionalProperty']


re_ns_n = re.compile(r'(.*[/#])(.*)')


class rdfsSubject(rdfSubject):
    
    def _splitname(self):
        return re.match(r'(.*[/#])(.*)',self.resUri).groups()
    
    @classmethod
    def ClassInstances(cls):
        """return a generator for instances of this rdf:type
        you can look in MyClass.rdf_type to see the predicate being used"""
        # Start with all things of "my" type in the db
        beenthere = set([])
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
        dbSubClasses = rdfsClass(cls.rdf_type).transitive_subClasses
        moreSubClasses = [dbsub.resUri for dbsub in dbSubClasses 
                                if dbsub.resUri not in [pysub.rdf_type for pysub in pySubClasses]]
        for sub in moreSubClasses:
            for i in cls.db.subjects(RDF.type, sub):
                if '' and not i in beenthere:
                    yield i
                    beenthere.add(i)        
        
        

class rdfsClass(rdfsSubject):
    """rdfSbject with some RDF Schema addons
    *Some* inferencing is implied
    Bleading edge: be careful"""
    rdf_type = RDFS.Class
    comment = rdfSingle(RDFS.comment)
    label = rdfSingle(RDFS.label)    
    subClassOf = rdfMultiple(RDFS.subClassOf, range_type = RDFS.Class)
    
    @property
    def transitive_subClassOf(self):
        return [rdfsClass(s) for s in self.db.transitive_objects(self.resUri,RDFS.subClassOf)]

    @property
    def transitive_subClasses(self):
        return [rdfsClass(s) for s in self.db.transitive_subjects(RDFS.subClassOf, self.resUri)]

    @property
    def properties(self):
        return list(rdfsProperty.filter_by(domain=self.resUri))
    
    def _emit_rdfSubject(self, visitedNS={}, visitedClass=set([])):
        """Procude the text that might be used for a .py file 
        TODO: This code should probably move into the commands module since that's the only place it's used"""
        ns,loc = self._splitname()
        prefix, qloc = self.db.qname(self.resUri).split(':')
        prefix = prefix.upper()
        
        if not visitedNS:
            src = """
from rdfalchemy import rdfSubject, Namespace, URIRef
from rdfalchemy.rdfsSubject import rdfsSubject
from rdfalchemy.orm import mapper

"""
            for k,v in self.db.namespaces():
                visitedNS[str(v)] = k.upper()
                src += '%s = Namespace("%s")\n' % (k.upper(),v)
        else:
            src = ""
        
        mySupers = []
        for mySuper in self.subClassOf:
            sns, sloc = mySuper._splitname()
            if ns == sns:
                src += mySuper._emit_rdfSubject(visitedNS=visitedNS)
                mySupers.append( sloc )
                
                
                
        mySupers = ",".join(mySupers) or "rdfsSubject"
        src += '\nclass %s(%s):\n'%(loc, mySupers)
        src += '\t"""%s %s"""\n'%(self.label, self.comment)
        src += '\trdf_type = %s["%s"]\n' % (visitedNS[ns],loc)
            
            
        for p in self.properties:
            pns, ploc = p._splitname()
            ppy = '%s["%s"]' % (visitedNS[pns],ploc)
            try:
                assert  str(p.range[RDF.type].resUri).endswith('Class') # rdfs.Class and owl.Class
                rns, rloc = rdfsSubject(p.range)._splitname()
                range_type = ', range_type = %s["%s"]' % (visitedNS[rns],rloc)
            except Exception, e:
                range_type = ''
            src += '\t%s = rdfMultiple(%s%s)\n' % (ploc.replace('-','_') ,ppy,range_type)
            
        # Just want this once at the end
        src.replace("mapper()\n","")        
        src += "mapper()\n"
                   
        return src
    
class rdfsProperty(rdfsSubject):
    rdf_type = RDF.Property
    domain = rdfSingle(RDFS.domain, range_type=RDFS.Class)
    range = rdfSingle(RDFS.range)
    subPropertyOf = rdfMultiple(RDFS.subPropertyOf)
    default_descriptor = rdfMultiple  #
        
class owlObjectProperty(rdfsProperty):
    rdf_type = OWL.ObjectProperty
    range = rdfSingle(RDFS.range, range_type = RDFS.Class)
    default_descriptor = rdfMultiple
        
class owlDatatypeProperty(rdfsProperty):
    rdf_type = OWL.DatatypeProperty
    default_descriptor = rdfMultiple
        
class owlFunctionalProperty(rdfsProperty):
    rdf_type = OWL.FunctionalProperty
    default_descriptor = rdfSingle
        
class owlInverseFunctionalProperty(rdfsProperty):
    rdf_type = OWL.InverseFunctionalProperty
    default_descriptor = rdfSingle
        
    
    
# this maps the return type of subClassOf back to rdfsClass
mapper()       

