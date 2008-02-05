from sparql import SPARQLGraph

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

class SesameGraph(SPARQLGraph):
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
        """context list ... pretty slow"""
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

    def __len__(self):
        """Returns the number of triples in the graph
        calls http://{self.url}/size  very fast
        """
        return int(urlopen(self.url+"/size").read())

    def set(self, (subject, predicate, object)):
        """Convenience method to update the value of object

        Remove any existing triples for subject and predicate before adding
        (subject, predicate, object).
        """
        self.remove((subject, predicate, None))
        self.add((subject, predicate, object))

             
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
            # 204 is actually the "success" code
            if e.code == 204:
                return
            else:
                log.error(e) 
        return result


    def load(self, source, publicID=None, format="xml"):
        self.parse(source, publicID, format)

