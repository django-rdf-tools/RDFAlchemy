#!/usr/bin/env python
import sys
import re

def setup_python3():
    # Taken from "distribute" setup.py
    from distutils.filelist import FileList
    from distutils import dir_util, file_util, util, log
    from os.path import join
  
    tmp_src = join("build", "src")
    log.set_verbosity(1)
    fl = FileList()
    for line in open("MANIFEST.in"):
        if not line.strip():
            continue
        fl.process_template_line(line)
    dir_util.create_tree(tmp_src, fl.files)
    outfiles_2to3 = []
    for f in fl.files:
        outf, copied = file_util.copy_file(f, join(tmp_src, f), update=1)
        if copied and outf.endswith(".py"):
            outfiles_2to3.append(outf)
  
    util.run_2to3(outfiles_2to3)
  
    # arrange setup to use the copy
    sys.path.insert(0, tmp_src)
  
    return tmp_src

kwargs = {}
if sys.version_info[0] >= 3:
    from setuptools import setup
    kwargs['use_2to3'] = True
    kwargs['src_root'] = setup_python3()
else:
    try:
        from setuptools import setup
        kwargs['test_suite'] = "nose.collector"
    except ImportError:
      try:
        from ez_setup import use_setuptools
        use_setuptools()
        from setuptools import setup
      except ImportError:
          from distutils.core import setup


# Find version. We have to do this because we can't import it in Python 3 until
# its been automatically converted in the setup process.
def find_version(filename):
    _version_re = re.compile(r'__version__ = "(.*)"')
    for line in open(filename):
        version_match = _version_re.match(line)
        if version_match:
            return version_match.group(1)

__version__ = find_version('rdfalchemy/__init__.py')

setup(
    name='RDFAlchemy',
    version=__version__,
    description="rdflib wrapper",
    author='Philip Cooper',
    author_email='philip.cooper@openvest.com',
    url="http://www.openvest.com/trac/wiki/RDFAlchemy",
    download_url="http://www.openvest.com/public/downloads/RDFAlchemy-%s.tar.gz"%__version__,
    install_requires=["rdflib"],
    packages=['rdfalchemy',
              'rdfalchemy/engine',
              'rdfalchemy/samples',
              'rdfalchemy/sparql',
              ],
    include_package_data=True,
    keywords = "RDF SPARQL",
    entry_points = {
        'console_scripts': [
            'sparql = rdfalchemy.sparql.script:main',
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
      * SQLAlchemy is an **ORM** (Object Relational Mapper) for relational databases
      
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
  
  c = Company.query.get_by(symbol = 'IBM')
  print("%s has an SEC symbol of %s" % (c.companyName, c.cik))

Includes advanced descriptors for read/write access to lists and collections.
      
.. _rdflib: https://github.com/RDFLib/rdflib
.. _Sesame: http://www.openrdf.org
.. _SPARQL: http://www.w3.org/TR/rdf-sparql-query/
    """

)
