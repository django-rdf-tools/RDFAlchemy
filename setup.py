try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

from rdfalchemy import __version__

setup(
    name='RDFAlchemy',
    version=__version__,
    description="rdflib wrapper",
    author='Philip Cooper',
    author_email='philip.cooper@openvest.com',
    url="http://www.openvest.com/trac/wiki/RDFAlchemy",
    download_url="http://www.openvest.com/public/downloads/RDFAlchemy-%s.tar.gz"%__version__,
    install_requires=["rdflib>=2.4.0","rdflib<=2.4.9"],
    packages=find_packages(exclude=['ez_setup']),
    include_package_data=True,
    keywords = "RDF SPARQL",
    entry_points = {
        'console_scripts': [
            'sparql = rdfalchemy.sparql.script:main',
            ],
        'paste.paster_command' : [
            'rdfSubject = rdfalchemy.commands:rdfSubjectCommand',
            ],
    },
    platforms = ["any"],
    classifiers = ["Programming Language :: Python",
                   "License :: OSI Approved :: BSD License",
                   "Topic :: Software Development :: Libraries :: Python Modules",
                   "Operating System :: OS Independent",
                   "Natural Language :: English",
                   ],
    long_description = """RDFAlchemy is an abstraction layer, allowing python
developers to use familiar *dot notation* to access and update an rdf triplestore.
    
      * RDFAlchemy is an **ORM** (Object Rdf Mapper) for graph data as:
      * SQLAlchemy is an **ORM** (Object Relational Mapper) for relalational databases
      
Allows access to:
    
      * rdflib_ datastores
      * Sesame_ Repositories
      * SPARQL_ endpoints
  
Provides intuitive access to RDF values by accessing predicate values 
through dot notation. ::    


  ov = Namespace('http://owl.openvest.org/2005/10/Portfolio#')
  
  class Company(rdfSubject):
    rdf_type = ov.Company
    symbol = rdfSingle(ov.symbol,'symbol')  #second param is optional
    cik = rdfSingle(ov.secCik)
    companyName = rdfSingle(ov.companyName)
  
  c = Company.get_by(symbol = 'IBM')
  print "%s has an SEC symbol of %s" % (c.companyName, c.cik)

Includes advanced descriptors for read/write access to lists and collections.
      
.. _rdflib: http://rdflib.net
.. _Sesame: http://www.openrdf.org
.. _SPARQL: http://www.w3.org/TR/rdf-sparql-query/
    """

)
