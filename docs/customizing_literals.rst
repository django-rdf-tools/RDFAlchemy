.. _literals_in_rdfalchemy: Literals in RDFAlchemy

======================
Literals in RDFAlchemy
======================

RDFAlchemy now imports ``Literal`` from its own file rather than rdflib.  This is to provide some customized handling of literals.  You can edit your :class:`~rdfalchemy.Literal` file or use the :class:`~rdfalchemy.Literal` source as a model for your own project.

Literal to Python
^^^^^^^^^^^^^^^^^
For Literals being coverted to Python (i.e. things coming out of the triplestore into your code) rdflib provides a :meth:`~rdfalchemy.Literal.bind` method to rebind an XSD datatype to a Python conversion function.

decimal
-------
**The problem:** Openvest projects originated from the world of finance and investments.  Accounting apps especially, need things to add up. That makes the default use of the ``float`` type troublesome.  Take for example:

.. code-block:: pycon

    >>> payments=[.1, .1, .1, -.3]
    >>> sum(payments) == 0
    False
    >>> #because
    ... payments # are floating point numbers like:
    [0.10000000000000001, 0.10000000000000001, 0.10000000000000001, -0.29999999999999999]


Literal to Python
^^^^^^^^^^^^^^^^^
The fix here is pretty simple.  Just import ``Decimal`` from the Python ``decimal`` module and bind it to the datatype.

.. code-block:: python

    from rdflib import Namespace, Literal
    from decimal import Decimal
    from rdflib.Literal import bind as bindLiteral  

    XSD = Namespace(u'http://www.w3.org/2001/XMLSchema#')

    bindLiteral(XSD.decimal,Decimal)

Python to Literal
^^^^^^^^^^^^^^^^^

datetime
---------
**The problem:** Currently (rdflib2.4 on OSX or Linux) cannot round trip a ``datetime`` Literal.  The problem is in the method that parses a string back into a python ``datetime`` object.  It doesn't like microseconds.  

.. code-block:: pycon

    >>> from rdflib import Literal, Namespace
    >>> from datetime import datetime
    >>> XSD_NS = Namespace(u'http://www.w3.org/2001/XMLSchema#')
    >>> Literal('2008-02-09T10:46:29', datatype=XSD_NS.dateTime).toPython()
    datetime.datetime(2008, 2, 9, 10, 46, 29)
    >>> # OK that worked but:
    ... Literal('2008-02-09T10:46:29.234', datatype=XSD_NS.dateTime).toPython() # should return a python datetime not a literal
    rdflib.Literal('2008-02-09T10:46:29.234', language=None, datatype=rdflib.URIRef('http://www.w3.org/2001/XMLSchema#dateTime'))

Literal to Python
^^^^^^^^^^^^^^^^^
A better parsing function has been added that you can view :class:`~rdfalchemy.Literal`.  This parser will handle microseconds and even slightly mangled iso strings.  

This same approach could be used  if you prefered to have the ``mx.DateTime`` moudule and work with ``mx.DateTime`` instances rather than datetime. 

Pick the parser you prefer and perform a binding as shown above for ``Decimal``.

