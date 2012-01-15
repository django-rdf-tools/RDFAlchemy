.. _sparql: SPARQL endpoints 

================
SPARQL Endpoints
================

.. automodule:: rdfalchemy.sparql

SPARQLGraph
===========
.. warning:: **early alpha code at work there.**  Works by providing read-only access.  

This module can be imported separately::

    from rdfalchemy.sparql import SPARQLGraph

It is not dependent on the rest of RDFAlchemy and so you can use 
it as a drop-in replacement for many :class:`rdflib.graph.ConjunctiveGraph` applications. 

Ported methods include:

 * :meth:`~rdfalchemy.sparql.SPARQLGraph.triples` including derivative methods like:
    * :meth:`~rdfalchemy.sparql.SPARQLGraph.subjects`, 
      :meth:`~rdfalchemy.sparql.SPARQLGraph.predicates`, 
      :meth:`~rdfalchemy.sparql.SPARQLGraph.objects`
    * :meth:`~rdfalchemy.sparql.SPARQLGraph.predicate_objects`, 
      :meth:`~rdfalchemy.sparql.SPARQLGraph.subject_predicates`, etc.
    * :meth:`~rdfalchemy.sparql.SPARQLGraph.value`

The following update methods will **not** work for SPARQL Endpoints because 
they are read only (see `Sesame <#Sesame>`_ below)

 * :meth:`~rdflib.graph.ConjunctiveGraph.add` and 
   :meth:`~rdflib.graph.ConjunctiveGraph.remove` including derivatives 
   like :meth:`~rdflib.graph.ConjunctiveGraph.set`
 * :meth:`~rdflib.graph.ConjunctiveGraph.parse` and 
   :meth:`~rdflib.graph.ConjunctiveGraph.load`, including the ability 
   to load from a url

 `SELECT`::
    Returns a generator of tuples for each return result

 `CONSTRUCT`::
    Returns an rdflib ``ConjunctiveGraph('IOMemory')`` instance which can be:
        * queried through the rdflib api
        * assigned as the `db` element to an rdfSubject instance
        * serialized to 'n3' or 'rdf/xml' 

.. autoclass:: rdfalchemy.sparql.SPARQLGraph
    :members:

Sesame endpoints
----------------
Can provide read access of Sesame through endpoints.  `SELECT` and 
`CONSTRUCT` methods supported.

If you know you have a Sesame2 endpoint then use the 
:class:`~rdfalchemy.sparql.sesame2.SesameGraph` rather than 
:class:`~rdfalchemy.sparql.sesame2.SPARQLGraph` as it has different capabilities.
 
Joseki endpoints
----------------
Can provide read access of Sesame through endpoints.  `SELECT`, 
`CONSTRUCT`, and `DESCRIBE` methods supported.

 `triples`::
    works but does not currently operate as a true stream.  Therefore:

    .. code-block:: python

        db.triples((None,None,None)) 
    
    will attempt to load the entire endpoint into a memory resident graph and **then** iterate over the results.

Relational Data thru SPARQL
----------------------------
In general if your data is in a relational database, you will probably 
want to use SQLAlchemy as your ORM.  If, however that data is in a 
relational table (yours or someone else's) across the web, and has a 
SPARQL Mapper on top of it, RDFAlchemy becomes your tool.  

D2R Server
^^^^^^^^^^
`D2R Server <http://sites.wiwiss.fu-berlin.de/suhl/bizer/d2r-server/>`_ 
includes a Joseki servelet.  If you depoloy a D2R Server you can access 
your relational database table through the web as an RDF datastore. 
RDFAlchemy usage looks like SQLAlchemy but now it can reach across the 
web into your RDBMS (PostgreSQL, MySQL, Oracle, db2 etc).


SesameGraph
============
The RDFAlchemy trunk now includes access to  `openrdf Sesame2 <http://www.openrdf.org>`_ 
datastores.  SesameGraph is a subclass of SPARQLGraph and builds on SPARQL endpoint 
capabilities as it provides write access via a `Sesame2 HTTP Protocol 
<http://www.openrdf.org/doc/sesame2/system/ch08.html>`_.  

Just pass the url of the Sesame2 repository endpoint and from there you can 
use an rdflib type API or use the returned graph in 
:class:`~rdfalchemy.rdfSubject.rdfSubject` as you would any rdflib database.

This module can be imported separately::

    from rdfalchemy.sparql.sesame2 import SesameGraph

it as a drop-in replacement for many :class:`rdflib.graph.ConjunctiveGraph` applications. 

Ported methods include:

 * :meth:`~rdfalchemy.sparql.SesameGraph.triples` including derivative methods like:
    * :meth:`~rdfalchemy.sparql.SesameGraph.subjects`, 
      :meth:`~rdfalchemy.sparql.SesameGraph.predicates`, 
      :meth:`~rdfalchemy.sparql.SesameGraph.objects`
    * :meth:`~rdfalchemy.sparql.SesameGraph.predicate_objects`, 
      :meth:`~rdfalchemy.sparql.SesameGraph.subject_predicates`, etc.
    * :meth:`~rdfalchemy.sparql.SesameGraph.value`
    * :meth:`~rdfalchemy.sparql.SesameGraph.add` 
      :meth:`~rdfalchemy.sparql.SesameGraph.remove`
      :meth:`~rdfalchemy.sparql.SesameGraph.set`
    * :meth:`~rdfalchemy.sparql.SesameGraph.parse` and 
      :meth:`~~rdfalchemy.sparql.SesameGraph.load`, including the ability 
      to load from a url

.. code-block:: python

    from rdfalchemy.sesame2 import SesameGraph
    from rdflib import Namespace 

    doap = Namespace('http://www.w3.org/1999/02/22-rdf-syntax-ns#doap')
    rdf = Namespace('http://www.w3.org/1999/02/22-rdf-syntax-ns#')

    db = SesameGraph('http://localhost:8080/sesame/repositories/testdoap')
    db.load('data/rdfalchemy_doap.rdf')
    db.load('http://doapspace.org/doap/some_important.rdf')

    project = db.value(None,doap.name,Literal('rdflib'))
    for p,o in db.predicate_objects(project):
       print('%-30s = %s'%(db.qname(p),o))


RDFAlchemy use of Sesame
------------------------ 
You can use it as you would any rdflib database.
Near the head of your code, place a  call like 

.. code-block:: python

    from rdfalchemy.sesame2 import SesameGraph
    rdfSubject.db = SesameGraph('http://some-place.com/repository')



Sesame2 Graph
-------------
.. autoclass:: rdfalchemy.sparql.sesame2.SesameGraph
    :members:

Parsers
=======
.. autoclass:: rdfalchemy.sparql.parsers._JSONSPARQLHandler
    :members:
.. autoclass:: rdfalchemy.sparql.parsers._XMLSPARQLHandler
    :members:
.. autoclass:: rdfalchemy.sparql.parsers._BRTRSPARQLHandler
    :members:

 