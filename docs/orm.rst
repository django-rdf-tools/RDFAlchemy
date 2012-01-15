.. _orm: RDFAlchemy ORM

==============
RDFAlchemy ORM
==============

rdfSubject
==========
.. automodule:: rdfalchemy.rdfSubject
.. autoclass:: rdfalchemy.rdfSubject.rdfSubject
    :members:

rdfsSubject
===========
.. automodule:: rdfalchemy.rdfsSubject
.. autoclass:: rdfalchemy.rdfsSubject.rdfsSubject
    :members:


Descriptors
===========

Understanding Descriptors is key to using RDFAlchemy.  A descriptor binds 
an instance variable to the calls to the RDF backend storage. 

Class definitions are simple with the RDFAlchemy Descriptors.  The descriptors are 
implemented with caching along the lines of `this recipe <http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/276643>`_.  
The predicate must be passed in.

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

.. note:: In addition to the ``get_by``, which returns a single instance, there is now a ``filter_by`` which returns a list of instances.

The RDFAlchemy Descriptors
---------------------------
.. autofunction:: rdfalchemy.descriptors.rdfSingle
.. autofunction:: rdfalchemy.descriptors.rdfMultiple
.. autofunction:: rdfalchemy.descriptors.rdfList
.. autofunction:: rdfalchemy.descriptors.rdfContainer
.. autofunction:: rdfalchemy.descriptors.owlTransitive

Returned values
----------------
* :class:`~rdfalchemy.descriptors.rdfSingle` returns a single literal
* :class:`~rdfalchemy.descriptors.rdfMultiple` returns a list (may be a list of one)
* :class:`~rdfalchemy.descriptors.rdfMultiple` will return a python list if the predicate is:
    * in multiple triples for the ``(s p o1)(s p o2)`` etc yields ``o2 <o1,> _``
    * points to an RDF Collection (``rdf:List``)
    * points to an RDF Container (``rdf:Seq``, ``rdf:Bag`` or ``rdf:Alt``)
* :class:`~rdfalchemy.descriptors.rdfList` returns a list (may be a list of one) and on save will save as an ``rdf:Collection`` (aka List)
* :class:`~rdfalchemy.descriptors.rdfContainer` returns a list and on save will save as an ``rdf:Seq``.

Chained descriptors
-------------------
The ``__init__`` functions for the Descriptors now takes an optional argument of ``range_type``. If you know the rdf.type (meaning the uriref of the type) you may pass it to the ``Class.__init__``.

Within the samples module, a ``DOAP.Project`` maintainer is a ``FOAF.Person`` 

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
 3. Call the :func:`~rdfalchemy.orm.mapper` function from `rdfalchemy.orm`.  This can be called later to 'remap' classes at any time.  

The bindings are not created until the third step so classes and descriptors can be created in any order.   

Chained predicates
------------------
Predicates can now be chained as in 

.. code-block:: python

    c = Company.query.get_by(symbol='IBM')
    print(c[vcard.adr][vcard.region])
    ## or
    print(c.address[vcard.region])

This works because the generic ``rdfSubject[predicate.uri]`` notation maps to ``rdfSubject.__getitem__`` which endeavors to return an instance of :class:`~rdfalchemy.rdfSubject.rdfSubject`.


Mapper
======

.. autofunction:: rdfalchemy.orm.mapper
.. autofunction:: rdfalchemy.orm.allsub

Hybrid SQL/RDF Alchemy Objects
==============================

If we look at the requirements for any python based object to respond to 
RDFAlchemy requests there are only two requirements:

1. That some instance object ``inst`` be able to respond to an ``inst.resUri`` 
call (it needs to know its URI) 
2. That there be some descriptor (like :class:`~rdfalchemy.descriptors.rdfSingle`) defined for the instance ``obj`` or its class ``type(obj)``

The first requirement could be satisfied by creating some type of mixin class 
and inheriting from multiple base objects.  Maybe I'll go there some day but 
the behavior of ``get_by`` would be uncertain (unless I reread the precedence 
rules :-).  In the mean time we can assign or lookup the relevant URI for the 
object (assignment could be defined via the 
`D2Rq <http://sites.wiwiss.fu-berlin.de/suhl/bizer/D2RQ/>`_ vocabulary).

From there you can assign descriptors on the fly and access your Triplestore.  
RDFDescriptors pull from the RDF Triplestore like rdf via RDFAlchemy and the 
rest pull from the relational database via SQLAlchemy.  A developer need not 
put all of his data in one repository.  

You can mix and match SQL, RDF and SPARQL data with little effort.

FormAlchemy
===========

See :mod:`Formalchemy support for RDFAlchemy <formalchemy:formalchemy.ext.rdf>`
