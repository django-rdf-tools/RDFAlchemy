
#from rdflib import ConjunctiveGraph
from rdflib import Literal, BNode, Namespace, URIRef
from rdflib.syntax.parsers.ntriples import NTriplesParser

from urllib2 import urlopen, Request, HTTPError
from urllib import urlencode

import os, re, logging
import simplejson

log=logging.getLogger('rdfAlchemy')

RDF  =Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
RDFS =Namespace("http://www.w3.org/2000/01/rdf-schema#")

re_ns_n = re.compile('(.*[/#])(.*)')

class DumpSink(object):
   def __init__(self):
      self.length = 0

   def triple(self, s, p, o):
      self.length += 1
      self._triple=(s,p,o)

   def get_triple(self):
       return self._triple

class SesameGraph(object):
    """openrdf-sesame graph via http
    Uses the sesame2 HTTP communication protocol
    to provide rdflib type api
    constructor takes http endpoint and repository name
    e.g.
      SesameGraph('http://www.openvest.org:8080/sesame/repositories/Test')"""
    
    def __init__(self, url, context=None):
        self.url = url
        self.context=context
    
    def get_namespaces(self):
        """Namespaces dict"""
        try:
            return self._namespaces
        except:
            pass
        req = Request(self.url+'/namespaces')
        req.add_header('Accept','application/sparql-results+json')
        ret=simplejson.load(urlopen(req))
        bindings=ret['results']['bindings']
        self._namespaces = dict([(b['prefix']['value'],b['namespace']['value']) for b in bindings])
        return self._namespaces
    namespaces=property(get_namespaces)
        
    def get_contexts(self):
        """context list """
        try:
            return self._contexts
        except:
            pass
        req = Request(self.url+'/contexts')
        req.add_header('Accept','application/sparql-results+json')
        ret=simplejson.load(urlopen(req))
        bindings=ret['results']['bindings']
        self._contexts = [(b['contextID']['value']) for b in bindings]
        return self._contexts
    contexts=property(get_contexts)
    
    def _statement_encode(self, (s, p, o), context):
        """helper function to encode triples to sesame statement uri's"""
        query = {}
        url = self.url+'/statements'
        if s:
            query['subj'] = s.n3()
        if p:
            query['pred'] = p.n3()
        if o:
            query['obj']  = o.n3()
        if context:
	    ### TODO FIXME what about bnodes like _:adf23123
            query['context']  = "<%s>"%context
        if query:
            url = url+"?"+urlencode(query)
        return url

    def add(self, (s, p, o), context=None):
        """Add a triple with optional context"""
        url = self.url+'/statements'
        ctx = context or self.context
        if ctx:
            url = url+"?"+urlencode(dict(context=ctx))
        req = Request(url)
        req.data = "%s %s %s .\n" % (s.n3(), p.n3(), o.n3())
        req.add_header('Content-Type','text/rdf+n3')
        try:
            result = urlopen(req).read()
        except HTTPError, e:
            if e.code == 204:
                return
            else:
                log.error(e) 
        return result
        
    def remove(self, (s, p, o), context=None):
        """Remove a triple from the graph

        If the triple does not provide a context attribute, removes the triple
        from all contexts.
        """
        url = self._statement_encode((s, p, o), context)
        req = Request(url)
        req.get_method=lambda : 'DELETE'
        try:
            result = urlopen(req).read()
        except HTTPError, e:
            if e.code == 204:
                return
            else:
                log.error(e) 
        return result
        
    def triples(self, (s, p, o), context=None):
        """Generator over the triple store

        Returns triples that match the given triple pattern. If triple pattern
        does not provide a context, all contexts will be searched.
        """
        url = self._statement_encode((s, p, o), context)
        req = Request(url)
        req.add_header('Accept','text/plain') # N-Triples is best for generator (one line per triple)
        log.debug("Request: %s" % req.get_full_url())
        dumper=DumpSink()
        parser=NTriplesParser(dumper)
        
        for l in urlopen(req):
            log.debug('line: %s'%l)
            parser.parsestring(l)
            yield dumper.get_triple() 
            
    def set(self, (subject, predicate, object)):
        """Convenience method to update the value of object

        Remove any existing triples for subject and predicate before adding
        (subject, predicate, object).
        """
        self.remove((subject, predicate, None))
        self.add((subject, predicate, object))

    def subjects(self, predicate=None, object=None):
        """A generator of subjects with the given predicate and object"""
        for s, p, o in self.triples((None, predicate, object)):
            yield s

    def predicates(self, subject=None, object=None):
        """A generator of predicates with the given subject and object"""
        for s, p, o in self.triples((subject, None, object)):
            yield p

    def objects(self, subject=None, predicate=None):
        """A generator of objects with the given subject and predicate"""
        for s, p, o in self.triples((subject, predicate, None)):
            yield o

    def subject_predicates(self, object=None):
        """A generator of (subject, predicate) tuples for the given object"""
        for s, p, o in self.triples((None, None, object)):
            yield s, p

    def subject_objects(self, predicate=None):
        """A generator of (subject, object) tuples for the given predicate"""
        for s, p, o in self.triples((None, predicate, None)):
            yield s, o

    def predicate_objects(self, subject=None):
        """A generator of (predicate, object) tuples for the given subject"""
        for s, p, o in self.triples((subject, None, None)):
            yield p, o


    def value(self, subject=None, predicate=RDF.value, object=None,
              default=None, any=True):
        """Get a value for a pair of two criteria

        Exactly one of subject, predicate, object must be None. Useful if one
        knows that there may only be one value.

        It is one of those situations that occur a lot, hence this
        'macro' like utility

        Parameters:
        -----------
        subject, predicate, object  -- exactly one must be None
        default -- value to be returned if no values found
        any -- if True:
                 return any value in the case there is more than one
               else:
                 raise UniquenessError
        """
        retval = default

        if (subject is None and predicate is None) or \
                (subject is None and object is None) or \
                (predicate is None and object is None):
            return None
        
        if object is None:
            values = self.objects(subject, predicate)
        if subject is None:
            values = self.subjects(predicate, object)
        if predicate is None:
            values = self.predicates(subject, object)

        try:
            retval = values.next()
        except StopIteration, e:
            retval = default
        else:
            if any is False:
                try:
                    next = values.next()
                    msg = ("While trying to find a value for (%s, %s, %s) the "
                           "following multiple values where found:\n" %
                           (subject, predicate, object))
                    triples = self.triples((subject, predicate, object))
                    for (s, p, o) in triples:
                        msg += "(%s, %s, %s)\n" % (
                            s, p, o)
                    raise exceptions.UniquenessError(msg)
                except StopIteration, e:
                    pass
        return retval

    def label(self, subject, default=''):
        """Query for the RDFS.label of the subject

        Return default if no label exists
        """
        if subject is None:
            return default
        return self.value(subject, RDFS.label, default=default, any=True)

    def comment(self, subject, default=''):
        """Query for the RDFS.comment of the subject

        Return default if no comment exists
        """
        if subject is None:
            return default
        return self.value(subject, RDFS.comment, default=default, any=True)

    def items(self, list):
        """Generator over all items in the resource specified by list

        list is an RDF collection.
        """
        while list:
            item = self.value(list, RDF.first)
            if item:
                yield item
            list = self.value(list, RDF.rest)
            
    def qname(self,uri):
        """turn uri into a qname given self.namespaces"""
        for p,n in self.namespaces.items():
            if uri.startswith(n):
                return "%s:%s"%(p,uri[len(n):])
        return uri

    def parse(self, source, publicID=None, format="xml", method='POST'):
        """ Parse source into Graph

        Graph will get loaded into it's own context (sub graph). 
        Format defaults to xml (AKA rdf/xml). 
        The publicID argument is for specifying the logical URI 
        for the case that it's different from the physical source URI. 
        Returns the context into which  the source was parsed.
          POST method adds data in a context
          PUT method replaces data in a context
        """
        url = self.url+'/statements'
        if not source.startswith('http://'):
            source = 'file://'+os.path.abspath(os.path.expanduser(source))
        ctx = "<%s>" % (publicID or source)
        url = url+"?"+urlencode(dict(context=ctx))

        req = Request(url)
        req.get_method = lambda : method
        
        if format=='xml':
            req.add_header('Content-Type','application/rdf+xml')
        elif format=='n3':
            req.add_header('Content-Type','text/rdf+n3')
        else:
            raise "Unknown format: %s"% format
        
        req.data = urlopen(source).read()
        log.debug("Request: %s" % req.get_full_url())
        try:
            result = urlopen(req).read()
            log.debug("Result: "+result)
        except HTTPError, e:
            if e.code == 204:
                return
            else:
                log.error(e) 
        return result


    def load(self, source, publicID=None, format="xml"):
        self.parse(source, publicID, format)

    def query(self, strOrQuery, initBindings={}, initNs={}, DEBUG=False,processor="sparql"):
        """
        Executes a SPARQL query against this Graph
        strOrQuery - Is either a string consisting of the SPARQL query 
        initBindings - A mapping from a Variable to an RDFLib term (used as initial bindings for SPARQL query)
        initNS - A mapping from a namespace prefix to a namespace
        DEBUG - A boolean flag passed on to the SPARQL parser and evaluation engine
        processor - The kind of RDF query (must be 'sparql' or 'serql')
        """
	query = strOrQuery
        if initNs:
	    prefixes = ''.join(["prefix %s: <%s>\n"%(p,n) for p,n in initNs.items()])
	    query = prefixes + query
        
        query = dict(query=query,queryLn=processor)
        url = self.url+"?"+urlencode(query)
	req = Request(url)
	req.add_header('Accept','application/sparql-results+json')
        ret=simplejson.load(urlopen(req))
        bindings=ret['results']['bindings']
        for b in bindings:
            for var,val in b.items():
                type = val['type']
                if type=='uri':
		    b[var]=URIRef(val['value'])
		elif type == 'bnode':
		    b[var]=BNode(val['value'])
		elif type == 'literal':
		    b[var]=Literal(val['value'],datatype=val.get('datatype'),lang=val.get('xml:lang'))
		else:
		    raise AttributeError("Binding type error: %s"%(type))
                
        return bindings



