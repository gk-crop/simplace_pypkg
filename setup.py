'''
Created on 06.10.2015

@author: k
'''
from setuptools import setup
import os

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


jp = 'Jpype1'    

__version__ = ''
exec(open('simplace/_version.py').read())

setup(name='simplace',
      version=__version__,
      description='Interact with the simulation framework Simplace',
      long_description = read('README.rst'),
      url='http://www.simplace.net/',
      author='Gunther Krauss',
      author_email='guntherkrauss@ui-bonn.de',
      license='GPL3',
      packages=['simplace'],
      install_requires=[
          jp,
      ],
      classifiers=[
          'Development Status :: 4 - Beta',
          'Intended Audience :: Developers',
          'Intended Audience :: Science/Research',
          'Topic :: Scientific/Engineering',
          'Programming Language :: Python',
          'Programming Language :: Java'
          
      ],
      zip_safe=False)