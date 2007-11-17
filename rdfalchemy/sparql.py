from rdflib import ConjunctiveGraph

class SPARQLGraph(object):
    """provides (some) rdflib api via http to a SPARQL endpoint
    gives 'read-only' access to the graph
    constructor takes http endpoint and repository name
    e.g.
      SPARQLGraph('http://www.openvest.org:8080/sesame/repositories/Test')"""
    
    def __init__(self, url, context=None):
        self.url = url
        self.context=context
    

        
    def triples(self, (s, p, o), context=None):
        """Generator over the triple store

        Returns triples that match the given triple pattern. If triple pattern
        does not provide a context, all contexts will be searched.
        """
        self.url+'?'+urlencode(query='construct {?s ?p ?o} where {?s ?p ?o}')
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
        for p,n in db.namespaces.items():
            if uri.startswith(n):
                return "%s:%s"%(p,uri[len(n):])
        return uri


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

    def construct(self, strOrTriple, initBindings={}, initNs={}):
        """
        Executes a SPARQL Construct
        initBindings - A mapping from a Variable to an RDFLib term (used as initial bindings for SPARQL query)
        initNS - A mapping from a namespace prefix to a namespace
        """
        if isinstance(strOrTriple, str):
            query = strOrTriple
            if initNs:
                prefixes = ''.join(["prefix %s: <%s>\n"%(p,n) for p,n in initNs.items()])
                query = prefixes + query
        else:
            assert "NotImplimented"
        query = dict(query=query)
        
        url = self.url+"?"+urlencode(query)
        req = Request(url)
        req.add_header('Accept','application/rdf+xml')
        subgraph = ConjunctiveGraph()
        subgraph.parse(urlopen(req))
        return subgraph

    def describe(self, s_or_po, initBindings={}, initNs={}):
        """
        Executes a SPARQL describe of resource
        s_or_po is either:
        
          * a subject ... should be a URIRef
          * a tuple of (predicate,object) ... pred should be inverse functional
          * a describe query string
          
        initBindings - A mapping from a Variable to an RDFLib term (used as initial bindings for SPARQL query)
        initNS - A mapping from a namespace prefix to a namespace
        """
        if isinstance(s_or_po, str):
            query = s_or_po
            if initNs:
                prefixes = ''.join(["prefix %s: <%s>\n"%(p,n) for p,n in initNs.items()])
                query = prefixes + query
        elif isinstance(s_or_po, URIRef) or isinstance(s_or_po, BNode):
            query = "describe %s" % (s_or_po.n3())
        else:
            p,o = s_or_po
            query = "describe ?s where {?s %s %s}"%(p.n3(),o.n3())
        query = dict(query=query)
        
        url = self.url+"?"+urlencode(query)
        req = Request(url)
        req.add_header('Accept','application/rdf+xml')
        subgraph = ConjunctiveGraph()
        subgraph.parse(urlopen(req))
        return subgraph

