#!/usr/bin/env python
"""
rdfalchemy.py - a Simple API for RDF


Requires rdflib <http://www.rdflib.net/> version 2.3 ??.

"""

__license__ = """
Copyright (c) 2005-2007 Philip Cooper <Philip.Cooper@openvest.com>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
__version__ = "0.1dev"

from rdflib import ConjunctiveGraph
from rdflib import Literal, BNode, Namespace, URIRef
from itertools import chain
import re
import logging

console = logging.StreamHandler()
## console.setLevel(logging.DEBUG)    ## <- the debug level goes here
formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
console.setFormatter(formatter)
log=logging.getLogger('rdfAlchemy')
##log.setLevel(logging.DEBUG)
log.addHandler(console)

RDF  =Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
RDFS =Namespace("http://www.w3.org/2000/01/rdf-schema#")
OWL  =Namespace("http://www.w3.org/2002/07/owl#")

re_ns_n = re.compile('(.*[/#])(.*)')

# Look into caching as in:
# http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/276643
# Note: Non data descriptors (get only) lookup in obj.__dict__ first
#       Data descriptors (get and set) use the __get__ first

# helper function, might be somewhere in rdflib I need to look for it there
def getList(sub, pred=None, db=None):
    """Attempts to return a list from sub (subject that is)
    passed in if it is a Collection or a Container (Bag,Seq or Alt)"""
    if not db:
        if isinstance(sub,rdfObject):
            db=sub.db
        else:
            db=rdfObject.db
    if pred:
        if isinstance(sub, rdfObject):
            subUri=sub.resUri        
        base = db.value(subUri,pred,any=True)
    else:
        # if there was no predicate assume a base node was passed in
        base=sub
    if type(base) != BNode:
        # Doesn't look like a list or a collection, just return multiple values (or an error?)
        val=[o for o in db.objects(subUri, pred)]
        return val
    members=[]
    first = db.value(base, RDF.first)
    # OK let's work at returning a list if there is an RDF.first
    if first:
        while first:
            members.append(first)
            base = db.value(base, RDF.rest)
            first = db.value(base, RDF.first)
        return members
    # OK let's work at returning a Collection (Seq,Bag or Alt) if was no RDF.first
    else:
        i=1        
        first=db.value(base, RDF._1)
        if not first:
            raise AttributeError, "Not a list, or collection but another type of BNode"
        while first:
            members.append(first)
            i += 1
            first=db.value(base, RDF['_%d'%i])
        return members

class rdflibAbstract(object):
    """Abstract base class for descriptors
    Descriptors are to map class instance variables to predicates
    optional cacheName is where to store items
    range_type is the rdf:type of the range of this predicate"""
    def __init__(self, pred, cacheName=None, range_type=None):
        self.pred = pred
        self.name = cacheName or pred
        self.range_type = range_type
    
    @property
    def range_class(self):
        """return the class that this descriptor is mapped to through the range_type"""
        if self.range_type:
            try:
                return self._mappedClass
            except AttributeError:
                log.warn("Descriptor %s has range of: %s but not yet mapped"%(self, self.range_type))
                return rdfObject
        else:
            return rdfObject
                    
class rdflibSingle(rdflibAbstract):
    '''This is a Discriptor
    Takes a the URI of the predicate at initialization
    Expects to return a single item
    on Assignment will set that value to the 
    ONLY triple with that subject,predicate pair'''
    def __init__(self, pred, cacheName=None, range_type=None):
        super(rdflibSingle, self).__init__(pred, cacheName, range_type)
        
    def __get__(self, obj, cls):
        if obj is None:
            return self
        if self.name in obj.__dict__:
            return obj.__dict__[self.name]
        log.debug("Geting with descriptor %s for %s"%(self.pred,obj.resUri))
        val=obj.__getitem__(self.pred)        
        if isinstance(val, BNode) or isinstance(val,URIRef):
            val = self.range_class(val)
        obj.__dict__[self.name]= val
        return val
    
    def __set__(self, obj, value):
        log.debug("SET with descriptor value %s of type %s"%(value,type(value)))
        #setattr(obj, self.name, value)  #this recurses indefinatly
        obj.__dict__[self.name]= value
        if isinstance(value,Literal):
            o = value
        elif isinstance(value,str):
            o = Literal(value,)
        else:
            o = Literal('What?')
        obj.db.set((obj.resUri,self.pred, o))
        #return None
    
    def __delete__(self, obj):
        # if this is a bnode like a list or a container a lot more should 
        # be done ala getList above
        log.debug("DELETE with descriptor for %s on %s"%(self.pred, obj.resUri))        
        return obj.db.remove((obj.resUri,self.pred, None))

   
class rdflibMultiple(rdflibAbstract):
    '''This is a Discriptor    
       Expects to return a list of values (could be a list of one)'''
    def __init__(self, pred, cacheName=None, range=None):
        super(rdflibMultiple, self).__init__(pred, cacheName=None, range_type=None)
        
    def __get__(self, obj, cls):
        if obj is None:
            return self
        val=[o for o in obj.db.objects(obj.resUri, self.pred)]
        # check to see if this is a Container or Collection
        # if so, return collection as a list
        if len(val) == 1 \
           and (obj.db.value(o,RDF.first) or obj.db.value(o,RDF._1)): 
                  val=getList(obj, self.pred)
        val=[((isinstance(v,BNode) or isinstance(v,URIRef)) and self.range_class(v) or v) for v in val]
        setattr(obj, self.name, val)
        try:
            log.info("Geting %s for %s"%(obj.db.qname(self.pred),obj.db.qname(obj.resUri)))
        except:
            log.info("Geting %s for %s"%(self.pred,obj.resUri))
        return val


class rdfObject(object):
    db=ConjunctiveGraph()
    """Default graph for access to instances of this type"""
    rdf_type=None
    """rdf:type of instances of this class"""
    def __init__(self, resUri):
        if isinstance(resUri, rdfObject):
            self.resUri=resUri.resUri 
            self.db=resUri.db
        elif isinstance(resUri, BNode) or isinstance(resUri, URIRef):
            self.resUri=resUri
        elif resUri[0]=="<" and resUri[-1]==">":
            self.resUri=URIRef(resUri[1:-1])
        elif resUri.startswith("_:"):
            self.resUri=BNode(resUri[1:-1])
        else:
            raise AttributeError("cannot construct rdfObject from %s"%(str(resUri)))
            
        rdftype = list(self.db.objects(resUri, RDF.type))
        if len(rdftype)==1:
            self.namespace, trash = re_ns_n.match(rdftype[0]).groups()
            self.namespace=Namespace(self.namespace)
        elif isinstance(self.resUri,URIRef):
            ns_n =  re_ns_n.match(self.resUri)
            if ns_n:
                self.namespace, self.name = ns_n.groups()
                self.namespace=Namespace(self.namespace)
                
    def get_by(cls, **kwargs):
        """Class Method, returns a single instance of the class
        by a single kwarg.  the keyword must be a descriptor of the
        class.
        example:
            bigBlue = Company.get_by(symbol='IBM')

        OWL Note:
            the keyword should map to an rdf predicate
            that is of type owl:InverseFunctional"""
        if len(kwargs) != 1:
            raise ValueError("get_by did not want %i args"%(len(kwargs)))
        key,value = kwargs.items()[0]
        pred=cls.__dict__[key].pred
        uri=cls.db.value(None,pred,Literal(value))
        if uri:
            return cls(uri)
        else:
            raise LookupError("%s = %s not found"%(key,value))
    get_by=classmethod(get_by)
        
    def filter_by(cls, **kwargs):
        """Class method returns a generator over classs instances
        meeting the kwargs conditions.

        Each keyword must be a class descriptor

        filter by RDF.type == cls.rdf_type is implicit

        Order helps, the first keyword should be the most restrictive
        """
        filters = []
        for key,value in kwargs.items():
            try:
                pred=cls.__dict__[key].pred
            except LookupError :
                raise LookupError ("%s not a valid descriptor for %s" % (key,cls))
            # try to make the value be OK for the triple query as an object
            if isinstance(value, rdfObject):
                obj = rdfObject.resUri
            elif isinstance(value, URIRef) or isinstance(value,BNode):
                obj = value
            else:
                obj = Literal(value)
            filters.append((pred,obj))
        # make sure we filter by type
        if not (RDF.type,cls.rdf_type) in filters:
            filters.append((RDF.type,cls.rdf_type))
        pred, obj = filters[0]
        print "Checking %s, %s" % (pred,obj)
        for sub in cls.db.subjects(pred,obj):
            print "maybe %s" % sub
            for pred,obj in filters[1:]:
                print "Checking %s, %s" % (pred,obj)
                if not list(cls.db.triples((sub,pred,obj))):
                    print "Not %s" % s
                    continue
            yield cls(sub)
    filter_by=classmethod(filter_by)
        
    def ClassInstances(cls):
        """return a generator for instances of this rdf:type
        you can look in MyClass.rdf_type to see the predicate being used"""
        for i in cls.db.subjects(RDF.type, cls.rdf_type):
            yield cls(i)
    ClassInstances=classmethod(ClassInstances)

    def GetRandom(cls):
        """for develoment just returns a random instance of this class"""
        from random import randint
        xii=list(cls.ClassInstances())
        return xii[randint(0,len(xii)-1)]
    GetRandom=classmethod(GetRandom)
        
    def __repr__(self):
        return "<%s -> %s>"%(self.__class__, self.resUri)

    def __getitem__(self, pred):
        #log.debug("Geting with __getitem__ %s for %s"%(self.db.qname(pred),self.db.qname(self.resUri)))
        log.debug("Geting with __getitem__ %s for %s"%(pred,self.resUri))
        val=self.db.value(self.resUri,pred)
        if isinstance(val,Literal):
            val =  val.datatype and val.toPython() or unicode(val) 
        elif isinstance(val, BNode) or isinstance(val,URIRef): 
            val=rdfObject(val) 
        return val
        
    def ppo(self,db=None):
        """Like pretty print...
        Return a 'pretty predicate,object' of self
        returning all predicate object pairs with qnames"""
        db = db or self.db
        for p,o in db.predicate_objects(self.resUri):
            print "%20s = %s"% (db.qname(p),str(o))
