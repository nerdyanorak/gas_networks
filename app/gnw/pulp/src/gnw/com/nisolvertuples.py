# ==============================================================================
#
#   package         :   GasNetWorks (gnw) Python/pulp fuelled LP/MIP modeller 
#   author          :   Marc Roth (re04179)
#   version         :   $Id: nisolvertuples.py 1860 2009-09-07 12:09:18Z re04179 $
#   heading         :   $HeadURL: http://subversion.rwe.com/svn/s_and_v_projects/GasNetworks/trunk/app/gnw/pulp/src/gnw/com/nisolvertuples.py $
#
#   Description     :   COM interface sub-package
#
#   Creation Date   :   20Jul2009
#
#   Copyright       :   RWE Supply and Trading GmbH
#
# ==============================================================================
"""
gnw.com: provides niSolverTuples for testing gnw.com.network.COM_Network class 
"""
niSolverTuples = \
    (\
        (u'key', u'name', u'attr', (u'dims', 0, u'sizes', (), u'types', u'str'), u'data', u'XPRESS_REMOTE_CLIENT'),
        (u'key', u'attr', u'attr', (u'dims', 1, u'sizes', (3,), u'types', (u'NI',)), u'data',
            (\
                (u'key', u'MIPRELCUTOFF', u'attr', (u'dims', 0, u'sizes', (), u'types', u'float'), u'data', 0.0001),
                (u'key', u'MIPRELSTOP', u'attr', (u'dims', 0, u'sizes', (), u'types', u'float'), u'data', 0.0050000000000000001),
                (u'key', u'URL', u'attr', (u'dims', 0, u'sizes', (), u'types', u'str'), u'data', u'http://xpressprod.rwe.com:8080/csgb-xpress/services/XpressExecutionServer?wsdl')
            )
        )
    )
# ==============================================================================
#
#   Revision Control:
#
#   $Revision:: 1860                    $   Revision of last commit
#   $Author:: re04179                   $   Author of last commit
#   $Date:: 2009-09-07 14:09:18 +0200 (#$   Date of last commit
#
# ==============================================================================
