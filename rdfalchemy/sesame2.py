from sparql import SPARQLGraph

from rdflib import Literal, BNode, Namespace, URIRef
from rdflib.syntax.parsers.ntriples import NTriplesParser

from urllib2 import urlopen, Request, HTTPError
from urllib import urlencode
from struct import unpack

from rdfalchemy.exceptions import MalformedQueryError, QueryEvaluationError

import os
import simplejson
import logging

log=logging.getLogger(__name__)


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
    to provide rdflib type api constructor takes http endpoint and repository name
    e.g. SesameGraph('http://www.openvest.org:8080/sesame/repositories/Test')"""
    
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
        log.debug("opening url: %s\n  with headers: %s" % (req.get_full_url(), req.header_items()))        
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
        
    def query(self, strOrQuery, initBindings={}, initNs={}, resultMethod="brtr",processor="sparql"):
        """
        Executes a SPARQL query against this Graph
        
        :param strOrQuery: Is either a string consisting of the SPARQL query 
        :param initBindings: *optional* mapping from a Variable to an RDFLib term (used as initial bindings for SPARQL query)
        :param initNs: optional mapping from a namespace prefix to a namespace
        :param resultMethod: results query requested (must be 'xml', 'json' 'brtr') 
         xml streams over the result set and json must read the entire set  to succeed 
        :param processor: The kind of RDF query (must be 'sparql' or 'serql')
        """
        query = strOrQuery
        if initNs:
	    prefixes = ''.join(["prefix %s: <%s>\n"%(p,n) for p,n in initNs.items()])
	    query = prefixes + query
        log.debug("Query: %s"%(query))
        query = dict(query=query,queryLn=processor)
        url = self.url+"?"+urlencode(query)
        req = Request(url)
        if resultMethod == 'brtr':
            return self._sparql_results_brtr(req)
        elif resultMethod == 'json':
            return self._sparql_results_json(req)
        elif resultMethod == 'xml':
            return self._sparql_results_xml(req)
        else:
            raise "Unknown resultMethod: %s"%(resultMethod)
            
    def _sparql_results_brtr(self,req):
        """_sparql_results_brtr takes a Request
         returns an interator over the results"""
        var_names=[]
        bindings=[] 
        req.add_header('Accept','application/x-binary-rdf-results-table')
        log.debug("Request: %s" % req.get_full_url())
        return _BRTRSPARQLHandler(urlopen(req))

    def parse(self, source, publicID=None, format="xml", method='POST'):
        """
        Parse source into Graph

        Graph will get loaded into it's own context (sub graph). 
        Format defaults to xml (AKA rdf/xml). 

        :returns: Returns the context into which  the source was parsed.
        
        :param source: source file in the form of "http://....." or "~/dir/file.rdf"
        :param publicID: *optional* the logical URI if it's different from the physical source URI. 
        :param format: must be one of 'xml' or 'n3'
        :param method: must be one of
        
          * 'POST' -- method adds data to a context
          * 'PUT' -- method replaces data in a context
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

class _BRTRSPARQLHandler(object):
    """Handler for the sesame binary table format BRTR_
    
    .. _BRTR: http://www.openrdf.org/doc/sesame/api/org/openrdf/sesame/query/BinaryTableResultConstants.html
    """

    def __init__(self, stream):
        self.stream = stream
        if self.stream.read(4) <> 'BRTR': raise ParseError("First 4 bytes in should be BRTR")
        self.ver = self.readint() # ver of protocol
        self.ncols = self.readint()
        self.keys = tuple(self.readstr() for x in range(self.ncols))
        self.values = [None,]*self.ncols
        self.ns = {}
        
    def readint(self):
        return  unpack('>i',self.stream.read(4))[0]
    
    def readstr(self):
        l = self.readint()
        return self.stream.read(l).decode("utf-8")

    def __iter__(self):
        return self

    def next(self):
        for i in range(self.ncols):
            val = self.getval()
            if val == 1: # REPEAT
                continue
            self.values[i] = val             
        return tuple(self.values)

    def getval(self):
        while True:
            rtype = ord(self.stream.read(1))
            if rtype == 0: #NULL
                return None
            elif rtype == 1: #REPEAT
                return 1
            elif rtype == 2: #NAMESPACE     
                nsid = self.readint()
                url = self.readstr()
                self.ns[nsid] = url
            elif rtype == 3: # QNAME
                nsid = self.readint()
                localname = self.readstr()
                return URIRef(self.ns[nsid] + localname)
            elif rtype == 4: # URI
                return URIRef(self.readstr())
            elif rtype == 5: # BNODE
                return BNode(self.readstr())
            elif rtype == 6: # PLAIN LITERAL
                return Literal(self.readstr())
            elif rtype == 7: # LANGUAGE LITERAL
                lit = self.readstr()
                lang= self.readstr()
                return Literal(lit,lang=lang)
            elif rtype == 8: # DATATYPE LITERAL
                lit = self.readstr()
                datatype = self.getval()
                return Literal(lit,datatype=datatype)                
            elif rtype == 126: # ERROR
                errType = ord(self.stream.read(1))
                errStr = self.readstr()
                if errType == 1:
                    raise MalformedQueryError(errStr)
                elif errType == 2:
                    raise QueryEvaluationError(errStr)
                else:
                    raise errStr
            elif rtype == 127: # EOF
                raise StopIteration()
            else:
                raise ParseError("Undefined record type: %s" % rtype)
                
    
