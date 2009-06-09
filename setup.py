import os
from setuptools import setup, find_packages

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "django-vcstorage",
    version = "0.1",
    url = 'http://bitbucket.org/jezdez/django-vcstorage/',
    license = "BSD",
    description = "A Django app that provides file storage backends for Mercurial, Git and Bazaar by using anyvc.",
    long_description = read('README'),
    author = 'Jannis Leidel',
    author_email = 'jannis@leidel.info',
    packages = find_packages('src'),
    package_dir = {'': 'src'},
    classifiers = [
        'Development Status :: 4 - Beta',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
    ]
)
