==========
RDFAlchemy
==========

The goal of RDF Alchemy is to allow anyone who uses `python <http://www.python.org/>`_ to have a object type API access to an RDF Triplestore.  

The same way that:

  * `SQLAlchemy <http://www.sqlalchemy.org>`_ is an ``ORM`` (Object Relational Mapper) for relational database users
  * RDFAlchemy is an ``ORM`` (Object RDF Mapper) for semantic web users.

**News**
  Trunk now includes:
  
  * Read/Write access for collections and containers
  * Read access to SPARQL endpoints
  * Read/Write access to Sesame2
  * Cascading delete
  * chained descriptors and predicate range->class mapping

Related resources
=================

Installation
------------
RDFAlchemy is now available at `Pypi <http://pypi.python.org/pypi>`_: Just type

.. code-block:: bash

    $ easy_install rdfalchemy

If you don't have setuptools installed...well you should so `go get it 
<http://peak.telecommunity.com/DevCenter/EasyInstall>`_.  Trust me.

Code
----
Browse dev code at http://bitbucket.org/gjhiggins/rdfalchemy and see the current trunk and all history.

This is an actively developing project so bugs come and go. Get your svn access to the trunk at:

.. code-block:: bash

    $ hg clone http://bitbucket.org/gjhiggins/rdfalchemy  

User Group
-----------
You can now `visit rdfalchemy-dev <http://groups.google.com/group/rdfalchemy-dev>`_ at Google Groups.

Bugs can be reported at bitbucket if you have an openid to login.

API Docs
---------
There are epydoc API Docs at http://www.openvest.com/public/docs/rdfalchemy/api/. You can also use links there to browse source, but it might not be current with the trunk.

.. image:: _static/rdfa_overview_l1.png
    :alt: RDFALchemy overview
    :align: center

The use of persistent objects in RDFAlchemy will be as close as possible to what it would be in SQLAlchemy.  Code like:

.. code-block:: pycon

    >>> c = Company.query.get_by(symbol = 'IBM')
    >>> print(c.companyName)
    International Business Machines Corp.

This code does not change as the user migrates from SQLAlchemy to RDFAlchemy and back, lowering the bar for adoption of RDF based datastores.

Capabilities
------------

* SQLAlchemy interface
* Caching of data reads
* Access from multiple datastores:
   * `rdflib <http://code.google.com/p/rdflib.net>`_ (beta)
   * `SPARQL <http://www.w3.org/TR/rdf-sparql-query/>`_ endpoints (**alpha**)
       * `Joseki <http://www.joseki.org/>`_ based Jena access ('''alpha''')
       * `D2R-server <http://sites.wiwiss.fu-berlin.de/suhl/bizer/d2r-server/>`_ ('''alpha''')
   * Access to RDF triples from SQL databases through D2Rq

SQLAlchemy
-----------
SQLAlchemy was chosen over the other popular python ORM (`SQLObject <http://www.sqlobject.org/>`_) because:

1.  There appears to be a migration of some from SQLObject to SQLAlchemy.  This appears to be in part due to some of the more sophisticated SQL capability of SQLAlchemy.
2.  SQLAlchemy is being used in future releases of `trac <http://trac.openvest.org/about>`_ and `Pylons <http://pylonshq.org>`_, two systems in active use at Openvest.
3.  SQLAlchemy has a `line of demarcation <http://www.sqlalchemy.org/docs/03/tutorial.html#tutorial_twoinone>`_ between the SQL and ORM portions of the library.  RDFAlchemy similarly provides the rdflib api to SPARQL and Sesame graphs.

Descriptors
-----------
Understanding Descriptors is key to using RDFAlchemy.  A descriptor binds an instance variable to the calls to the RDF backend storage. 

Class definitions are simple with the rdflib Descriptors.  The descriptors are implemented with caching along the lines of `this recipe <http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/276643>`_.  The predicate must be passed in.   

.. code-block:: python

    ov = Namespace('http://owl.openvest.org/2005/10/Portfolio#')
    vcard = Namespace("http://www.w3.org/2006/vcard/ns#")

    class Company(rdfSubject):
        rdf_type = ov.Company
        symbol = rdfSingle(ov.symbol,'symbol')  #second param is optional
        cik = rdfSingle(ov.secCik)
        companyName = rdfSingle(ov.companyName)
        address = rdfSingle(vcard.adr)
        stock = rdfMultiple(ov.hasIssue)
    
    c = Company.query.get_by()
    print("%s has an SEC symbol of %s" % (c.companyName, c.cik))

Returned values
^^^^^^^^^^^^^^^
* :class:`rdfalchemy.descriptors.rdfSingle` returns a single literal
* :class:`rdfalchemy.descriptors.rdfMultiple` returns a list (may be a list of one)
* :class:`rdfalchemy.descriptors.rdfMultiple` will return a python list if the predicate is:
    * in multiple triples for the ``(s p o1)(s p o2)`` etc yields ``o2 <o1,> _``
    * points to an RDF Collection (rdf:List)
    * points to an RDF Container (rdf:Seq, rdf:Bag or rdf:Alt)
* :class:`rdfalchemy.descriptors.rdfList` returns a list (may be a list of one) and on save will save as an RDF:Collection (aka List)
* :class:`rdfalchemy.descriptors.rdfContainer` returns a list and on save will save as an RDF:Seq.

Chained predicates
------------------
Predicates can now be chained as in 

.. code-block:: python

    c = Company.query.get_by(symbol='IBM')
    print(c[vcard.adr][vcard.region])
    ## or
    print(c.address[vcard.region])

This works because the generic ``rdfSubject[predicate.uri]`` notation maps to ``rdfSubject.__getitem__`` which endeavors to return an instance of :class:`~rdfalchemy.rdfSubject.rdfSubject`.

Chained descriptors
^^^^^^^^^^^^^^^^^^^^^^^
The ``__init__`` functions for the Descriptors now takes an optional argument of ``range_type``. If you know the rdf.type (meaning the uriref of the type) you may pass it to the ``Class.__init__``.

Within the samples module, a DOAP.Project maintainer is a FOAF.Person 

.. code-block:: python

    DOAP=Namespace("http://usefulinc.com/ns/doap#")
    FOAF=Namespace("http://xmlns.com/foaf/0.1/" )

    class Project(rdfSubject):
        rdf_type = DOAP.Project
        name = rdfSingle(DOAP.name)
        # ... some other descriptors here
        maintainer = rdfSingle(DOAP.maintainer,range_type=FOAF.Person)

    from rdfalchemy.samples.foaf import Person
    from rdfalchemy.orm import mapper

    mapper()
    # some method to find an instance
    p = Doap.ClassInstances().next()
    p.maintainer.mbox

To get such mapping requires 3 steps:

 1. Classes must be declared with the proper `rdf_type` Class variable set 
 2. Descriptors that return an instance of a python class should be created with the optional parameter of range_type with the same type as in step 1.
 3. Call the `mapper()` function from `rdfalchemy.orm`.  This can be called later to 'remap' classes at any time.  

The bindings are not created until the third step so classes and descriptors can be created in any order.   

Hybrid SQL/RDF Alchemy Objects
-------------------------------

If we look at the requirements for any python based object to respond to RDFAlchemy requests there are only two requirements:

1. That some instance object `inst` be able to respond to an `inst.resUri` call (it needs to know it's URI) 
2. That there be some descriptor (like `rdfSingle()`) defined for the instance `obj` or its class `type(obj)`

The first requirement could be satisfied by creating some type of mixin class and inheriting from multiple base objects.  Maybe I'll go there some day but the behavior of get_by would be uncertain (unless I reread the precedence rules :-).  In the mean time we can assign or lookup the relevant URI for the object (assignment could be defined via the `D2Rq <http://sites.wiwiss.fu-berlin.de/suhl/bizer/D2RQ/>`_ vocabulary).

From there you can assign descriptors on the fly and access your Triplestore.  RDFDescriptors pull from the RDF Triplestore like rdf via RDFAlchemy and the rest pull from the relational database via SQLAlchemy.  A developer need not put all of his data in one repository.  

You can mix and match SQL, rdflib and SPARQL data with little effort.

CRUD
----

Create
^^^^^^

.. code-block:: python

    class Person(rdfSubject):
    	    rdf_type = FOAF.Person
    	    first = rdfSingle(FOAF.givenname)
    	    last = rdfSingle(FOAF.surname)
    	
    p1 = Person() # creates a bnode with an `foaf:Person <rdf:type>`_ triple
    p2 = Person('<http://www.openvest.com/user/phil') #creates a URIRef with the same triple
    p3 = Person(last="Cooper",first="Philip") #creates a bnode with 3 triples (rdf:type FOAF:surname FOAF:givenname)

Read
^^^^
Reading is simply a matter of using the declared descriptors  

.. code-block:: python

    c = Company.query.get_by(symbol = 'IBM')
    print(c.companyName)
    print(c.address.region)

If a descriptor is not defined for a predicate and you still want to access the value
you can use the `__getitem__` dictionary type access

.. code-block:: python

    print(c[ov.companyName])
    print(c[vcard.adr][vcard.region])

The flexibility of the item access is ok but descriptors should be used whenever possible as they 
are much more intelligent. They:

 * cache database calls
 * return the proper class of the returned item if `orm.mapper()` has been called
 * return lists correctly for collections (Lists, and Containers both)

Update
^^^^^^
Writing to the database for rdflib is done at the time of assignment. It currently only performs set or delete operations for `rdfSingle` descriptors as the behavior for `rdfMultiple` is more ambiguous.

The basic syntax for the :class:`~rdfalchemy.descriptors.rdfSingle` descriptors is:

.. code-block:: python

    ibm Company.query.get_by(symbol = 'IBM')
    sun Company.query.get_by(symbol = 'JAVA')

    ## add another descriptor on the fly
    Company.industry = rdfSingle(ov.yindustry,'industry')

    ## add an attribute (to the database)
    sun.industry = 'Computer stuff'

    ## delete an attribute (from the database)
    del ibm.industry

Delete
^^^^^^
To delete a record, use the ``remove()`` method.  Removing an object from a graph database is more complicated than removing the the triples where the item is the subject of the triple.  

.. code-block:: python

    def remove(self, node=None, db=None, cascade = 'bnode', bnodeCheck=True):
            """remove all triples where this rdfSubject is the subject of the triple
            db -- limit the remove operation to this graph
            node -- node to remove from the graph defaults to self
            cascade -- must be one of:
                        * none -- remove none
                        * bnode -- (default) remove all unreferenced bnodes
                        * all -- remove all unreferenced bnode(s) AND uri(s)
            bnodeCheck -- boolean 
                        * True -- (default) check bnodes and raise exception if there are
                                  still references to this node
                        * False -- do not check.  This can leave orphaned object reference 
                                   in triples.  Use only if you are resetting the value in
                                   the same transaction
            """

The important thing to understand here is that the default behavior is to cascade the delete recursively deleting all object nodes that are not the object of any other triples.  This correctly deletes all lists and containers and things like the maintainer triples for a DOAP record or the author records of a bibliographic item.


Utility methods
----------------
The RDFAlchemy api is starting to grow a little bit.

In addition to the ``get_by`` which returns a single instance there is now a ``filter_by`` which returns a list of instances.

For console users (you are using `iPython <http://ipython.scipy.org/>`_ aren't you?) you should check out the ``ppo`` method which dumps predicate object pairs to the console.

There is now a ``create_engine utility`` method in the engine submodule.

There is a samples submodule where some classes like ``Foaf`` and ``Doap`` will show sample usage of RDFAlchemy and a subdirectory where some rdf Schemes will be provided. 

Other RDF mappers
-----------------

`TRAMP <http://www.aaronsw.com/2002/tramp/>`_ from the mind of Aaron Swartz.  The clean use of rdflib Namespace type mapping is carried forward in RDFAlchemy.  

.. code-block:: python

    >>> c = Company.query.get_by(symbol = 'IBM')
    >>> print(c.companyName)
    International Business Machines Corp.
    >>>
    >>> from rdflib import Namespace
    >>> ov = Namespace('http://owl.openvest.org/2005/10/Portfolio#')
    >>> print(ov.companyName )
    http://owl.openvest.org/2005/10/Portfolio#companyName
    >>> print(c[ov.companyName])
    International Business Machines Corp.

This provides the user with complete flexibility.  Any predicate can be given using the `dict` style notation.  The predicate values can even be determined dynamically at run time.  


In `Sparta <http://www.mnot.net/sw/sparta/>`_  however, the Namespace prefix is brought forward into the attribute name.  Something like `c.ov_companyName`.  I don't like this and will not carry it forward.  If you know the prefix mapping and predicate name, use the TRAMP style dict access as above.  If you want pythonic dot notation access, you should use descriptors.  You can even declare them after the definition of the class as in 

.. code-block:: python

    Company.stockDescription = rdfSingle(ov.stockDescription,'stockDescription')
    print(c.stockDescription)


SPARQL Endpoints
===========================
.. warning:: **early alpha code at work there.**  Works by providing read-only access.  

Standalone use
--------------
This module can stand alone. **It is not dependent on the rest of RDFAlchemy**.  You can use it as a drop-in replacement for many :class:`rdflib.graph.ConjunctiveGraph` applications. 

Ported methods include:

 * `triples` including derivative methods like:
    * `subjects`, `predicates`, `objects`
    * `predicate_objects`, `subject_predicates`, etc.
    * `value`

The following update methods will **not** work for SPARQL Endpoints as they are read only (see `Sesame <#Sesame>`_ below)
 * `add` and `remove` including derivatives like:
    * `set`
 * `parse` and `load` including the ability to load from a url

 `SELECT`::
    Returns a generator of tuples for each return result

 `CONSTRUCT`::
    Returns an rdflib ``ConjunctiveGraph('IOMemory')`` instance which can be:
        * queried through the rdflib api
        * assigned as the `db` element to an rdfSubject instance
        * serialized to 'n3' or 'rdf/xml' 

Sesame endpoints
----------------
Can provide read access of Sesame through endpoints.  `SELECT` and `CONSTRUCT` methods supported.

If you know you have a Sesame2 endpoint use the :class:~rdfalchemy.sparql.sesame2.SesameGraph` rather than :class:~rdfalchemy.sparql.sesame2.SPARQLGraph` as it has different capabilities.
 
Joseki endpoints
----------------
Can provide read access of Sesame through endpoints.  `SELECT`, `CONSTRUCT`, and `DESCRIBE` methods supported.

 `triples`::
    works but does not currently operate as a true stream.  Therefore:

    .. code-block:: python

        db.triples((None,None,None)) 
    
    will attempt to load the entire endpoint into a memory resident graph and **then** iterate over the results.

Relational Data thru SPARQL
----------------------------
In general if your data is in a relational database, you will probably want to use SQLAlchemy as your ORM.  If, however that data is in a relational table (yours or someone else's) across the web, and has a SPARQL Mapper on top of it, RDFAlchemy becomes your tool.  


D2R Server
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
`D2R Server <http://sites.wiwiss.fu-berlin.de/suhl/bizer/d2r-server/>`_ includes a Joseki servelett.  If you depoloy a D2R Server you can access your relational database table through the web as an rdf datastore.  RDFAlchemy usage looks like SQLAlchemy but now it can reach across the web into your rdbms (postgres, mysql, oracle, db2 etc).

D2R Server is used internally at Openvest but there are other engines which should all be accessible through the RDFAlchemy SPARQL client.  

Other SPARQL / SQL maps
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Another active projects providing SPARQL access to relational databases are

    * `SquirrelRDF <http://jena.sourceforge.net/SquirrelRDF>`_. In addition to relational databases, SquirrelRDF also supports access to LDAP directories.
    * `Virtuoso <http://virtuoso.openlinksw.com/>`_ which seams to have use pretty smart rewriting algorithm and also supports Named Graphs.
    * `DartQuery <http://ccnt.zju.edu.cn/projects/dartgrid/intro.html>`_. DartQuery is a component of the DartGrid application framework which rewrites SPARQL queries as SQL against legacy relational databases.
    * `SPASQL <http://www.w3.org/2005/05/22-SPARQL-MySQL/>`_ is an open-source module compiled into the MySQL server to give MySQL native support for RDF.

Sesame
------
The RDFAlchemy trunk now includes access to `openrdf Sesame2 <http://www.openrdf.org>`_ datastores.  SesameGraph is a subclass of SPARQLGraph and builds on SPARQL endpoint capabilities as it provides write access via a `Sesame2 HTTP Protocol <http://www.openrdf.org/doc/sesame2/system/ch08.html>`_.  Just pass the url of the Sesame2 repository endpoint and from there you can use an rdflib type api or use the returned graph in :class:`~rdfalchemy.rdfSubject.rdfSubject` as you would any rdflib database.

Standalone use
--------------
This module can stand alone. **It is not dependent on the rest of RDFAlchemy**.  You can use it as a drop-in replacement for many :class:`rdflib.graph.ConjunctiveGraph` applications. 

Ported methods include:

 * `triples` including derivative methods like:
    * `subjects`, `predicates`, `objects`
    * `predicate_objects`, `subject_predicates` etc
    * `value`
 * `add` and `remove` including derivatives like:
    * `set`
 * `parse` and `load` including the ability to load from a url

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

Other Python SPARQL endpoints
------------------------------
Some of these have nice code which I hope to migrate into RDFAlchemy. For the impatient, you can check out:

 * http://ivanherman.wordpress.com/2007/07/06/sparql-endpoint-interface-to-python/ 
 * http://code.google.com/p/pysparql/source Nice use of pulldom to use a generator for large responses.
 * http://www.openrdf.org/forum/mvnforum/viewthread?thread=1393 Attempts to provide DB API 2.0 access.  The code looks incomplete but has some very nice use of reading the Sesame `binary results format <http://www.openrdf.org/doc/sesame/api/org/openrdf/sesame/query/BinaryTableResultConstants.html>`_ (`application/x-binary-rdf-results-table`)
 * http://www.w3.org/2001/sw/DataAccess/proto-tests/tools/ used for the w3c `SPARQL Implementation Report <http://www.w3.org/2001/sw/DataAccess/impl-report-protocol>`_

Jython
======
Not sure if the project is ready to branch.  If the Sesame2 HTTP access provided above is not enough and you need to access Sesame and/or Jena with python you and check out the `RDFAlchemyJython <wiki:RDFAlchemyJython>`_ page for some samples.

