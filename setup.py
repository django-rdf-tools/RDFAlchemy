try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

setup(
    name='RDFAlchemy',
    version="0.2",
    tag_dev=".dev",
    description="rdflib wrapper",
    author='Philip Cooper',
    author_email='philip.cooper@openvest.com',
    url="http://www.openvest.com/trac/wiki/RDFAlchemy",
    install_requires=["rdflib>=2.4.0"],
    packages=find_packages(exclude=['ez_setup']),
    include_package_data=True,
)
