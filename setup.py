try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

setup(
    name='RDFAlchemy',
    version="0.2b1",
    description="rdflib wrapper",
    author='Philip Cooper',
    author_email='philip.cooper@openvest.com',
    url="http://www.openvest.com/trac/wiki/RDFAlchemy",
    download_url="http://www.openvest.com/public/downloads/RDFAlchemy-0.2b1.tar.gz",
    install_requires=["rdflib==2.4.0"],
    packages=find_packages(exclude=['ez_setup']),
    include_package_data=True,
    keywords = "RDF SPARQL",
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
      * SPARQL endpoints
      
.. _rdflib: http://rdflib.net
.. _Sesame: http://www.openrdf.org
    """

)
