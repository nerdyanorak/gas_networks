# ==============================================================================
#
#   package         :   GasNetWorks (gnw) Python/pulp fuelled LP/MIP modeller 
#   author          :   Marc Roth (re04179)
#   version         :   $Id: setup.py 8019 2010-06-22 12:50:21Z re04179 $
#   heading         :   $HeadURL: http://subversion.rwe.com/svn/s_and_v_projects/GasNetworks/trunk/app/gnw/pulp/setup.py $
#
#   Description     :   Setup script for the gnw project package
#
#   Creation Date   :   24Mar2009
#
#   Copyright       :   RWE Supply and Trading GmbH
#
# ==============================================================================
"""
For building a
    - source distribution, run
        - > python setup.py sdist
    - binary distribution (egg format), run
        - > python setup.py bdist_egg
        (this is the preferred binary distribution container)
    - binary distribution (on RPM based systems), run
        - > python setup.py bdist_rpm
"""
import os
pathsep_char = os.pathsep
import sys
sys.path.insert(0, '.' + pathsep_char)

from gnw import __version__
from gnw import __authors__
from gnw import __copyright__

VERSION = __version__
AUTHORS = ""
for item in __authors__:
    AUTHORS += item + ", "
EMAILS = 'marc.roth@rwe.com'
LICENSE = "For use within RWE Supply and Trading GmbH only; " + __copyright__
PACKAGES = ['gnw', 'gnw.com']

from setuptools import setup, find_packages

setup( name='gnw',
       version=VERSION,
       url='http://www.rwetrading.com',
       description='A Python Gas NetWork optimisation package based on PuLP.',
       author=AUTHORS, 
       author_email=EMAILS,
       package_dir={'' : 'src'},
       packages=PACKAGES,
       license=LICENSE,
       zip_safe=True,
       install_requires=['fpconst>=0.7.2',
                         'numpy>=1.0.4',
                         'PuLP>=1.21',
                         'SOAPpy>=0.12'] )

# ==============================================================================
#
#   Revision Control:
#
#   $Revision:: 8019                    $   Revision of last commit
#   $Author:: re04179                   $   Author of last commit
#   $Date:: 2010-06-22 14:50:21 +0200 (#$   Date of last commit
#
# ==============================================================================
