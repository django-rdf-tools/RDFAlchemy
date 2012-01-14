.. RDFAlchemy documentation master file, created by

Welcome to RDFAlchemy's documentation!
======================================

Contents:

.. toctree::
   :maxdepth: 2

   rdfalchemy
   customizing_literals

Commands
========

.. autoclass:: rdfalchemy.commands.rdfSubjectCommand
    :members:

ORM
===
.. autofunction:: rdfalchemy.orm.mapper
.. autofunction:: rdfalchemy.orm.allsub

SPARQL
======
.. automodule:: rdfalchemy.sparql

Graphs
------

SPARQL Graph
^^^^^^^^^^^^
.. autoclass:: rdfalchemy.sparql.SPARQLGraph
    :members:

Sesame2 Graph
^^^^^^^^^^^^^^
.. autoclass:: rdfalchemy.sparql.sesame2.SesameGraph
    :members:

Parsers
-------
.. autoclass:: rdfalchemy.sparql.parsers._JSONSPARQLHandler
    :members:
.. autoclass:: rdfalchemy.sparql.parsers._XMLSPARQLHandler
    :members:
.. autoclass:: rdfalchemy.sparql.parsers._BRTRSPARQLHandler
    :members:

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

Engine room
===========
.. autofunction:: rdfalchemy.engine.engine_from_config
.. autofunction:: rdfalchemy.engine.create_engine

Descriptors
===========
.. autofunction:: rdfalchemy.descriptors.rdfSingle
.. autofunction:: rdfalchemy.descriptors.rdfMultiple
.. autofunction:: rdfalchemy.descriptors.rdfList
.. autofunction:: rdfalchemy.descriptors.rdfContainer
.. autofunction:: rdfalchemy.descriptors.owlTransitive

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

