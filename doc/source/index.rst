Simplace's documentation!
====================================

.. toctree::
   :maxdepth: 2
   
The package offers two interfaces to the simulation framework Simplace. 
 - Procedural interface with functions and procedures
 - Object oriented interface with objects and methods    

Procedural interface
--------------------

.. automodule:: simplace
   :members:


Object oriented interface
-------------------------

.. automodule:: SimplaceClasses
   :members:

Troubleshooting
================

Simplace requires the package JPype1.
If it is not installed automatically, try to install JPype manually. 
JPype1 optionally needs the package numpy. If you can't install numpy, then try to 
install JPype1 manually without numpy support. For Windows you can use binary packages
from http://www.lfd.uci.edu/~gohlke/pythonlibs/

You need also the Microsoft Visual C++ 2015 Redistributables. If they are not yet installed
on your system, you have to do it manually.

Simplace needs a Java virtual machine. If you have 64 bit version of Python, then 
you need also the 64 bit version of Java.

If you get an error loading the java virtual machine, check if the java location is configured
properly. There are different methods how python tries to detect the java virtual machine:

- JAVA_HOME environment variable
- Registry entry HKEY_LOCAL_MACHINE/SOFTWARE/JavaSoft/Java Runtime Environment/1.8[.xx]/RuntimeLib on Windows
- the symbolic link /usr/lib/jvm/default-java on Ubuntu
- ...

  
	
Indices and tables
==================

* :ref:`genindex`
* :ref:`search`

.. _changelog:

.. toctree::
   :maxdepth: 2
   :caption: Version history
   
   changelog
