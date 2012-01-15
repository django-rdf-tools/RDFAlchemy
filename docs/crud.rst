.. _crud: CRUD

====
CRUD
====

Create
======

.. code-block:: python

    class Person(rdfSubject):
    	    rdf_type = FOAF.Person
    	    first = rdfSingle(FOAF.givenname)
    	    last = rdfSingle(FOAF.surname)
    	
    p1 = Person() # creates a bnode with an `foaf:Person <rdf:type>`_ triple
    p2 = Person('<http://www.openvest.com/user/phil') #creates a URIRef with the same triple
    p3 = Person(last="Cooper",first="Philip") #creates a bnode with 3 triples (rdf:type FOAF:surname FOAF:givenname)

Read
====
Reading is simply a matter of using the declared descriptors  

.. code-block:: python

    c = Company.query.get_by(symbol = 'IBM')
    print(c.companyName)
    print(c.address.region)

If a descriptor is not defined for a predicate and you still want to access the value
you can use the ``__getitem__`` dictionary type access

.. code-block:: python

    print(c[ov.companyName])
    print(c[vcard.adr][vcard.region])

The flexibility of the item access is ok but descriptors should be used whenever possible as they 
are much more intelligent. They:

 * cache database calls
 * return the proper class of the returned item if :func:`~rdfalchemy.orm.mapper` has been called
 * return lists correctly for collections (Lists, and Containers both)

Update
======
Writing to the database for rdflib is done at the time of assignment. It 
currently only performs ``set`` or ``delete`` operations for :class:`~rdfalchemy.descriptors.rdfSingle` descriptors as the behavior for :class:`~rdfalchemy.descriptors.rdfMultiple` is more ambiguous.

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
======
To delete a record, use the ``remove()`` method.  Removing an object from a graph database is more complicated than removing the triples where the item is the subject of the triple.  

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

The important thing to understand here is that the default behavior is to 
cascade the delete recursively, deleting all object nodes that are not the 
object of any other triples.  This correctly deletes all lists and containers 
and things like the maintainer triples for a DOAP record or the author 
records of a bibliographic item.

