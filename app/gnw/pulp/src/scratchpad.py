# ==============================================================================
#
#   package         :   GasNetWorks (gnw) Python/pulp fuelled LP/MIP modeller 
#   author          :   Marc Roth (re04179)
#   version         :   $Id: scratchpad.py 500 2009-04-20 10:58:21Z re04179 $
#   heading         :   $HeadURL: http://subversion.rwe.com/svn/s_and_v_projects/GasNetworks/trunk/app/gnw/pulp/src/scratchpad.py $
#
#   Description     :   Package file
#
#   Creation Date   :   06Mar2009
#
#   Copyright       :   RWE Supply and Trading GmbH
#
# ==============================================================================
class aClass:
    m_dict = dict()
    def __init__(self, a_dict):
        self.m_dict.update(a_dict)



if __name__ == "__main__":
    import gnw
    print "gnw version:", gnw.__version__

    import numpy
    import pulp
    import sys
    
    a_dict = {1 : 'A',
              2 : 'B'}
    b_dict = {1 : 'C',
              3 : 'D',
              4 : 'E'}
    
    a = aClass( a_dict )
    
    for k,v in a.m_dict.iteritems():
        print "a:", k, "=", v
    print
    
    b = aClass( b_dict )
    
    for k,v in b.m_dict.iteritems():
        print "b:", k, "=", v
    print
    
    for k,v in aClass.m_dict.iteritems():
        print "aClass:", k, "=", v
    
    a2d_list = [[1,2,3.0], [3,4,5.0], [5,6,7.0], [7,8,9.0]]
    
    a2d_ndarray = numpy.array( a2d_list )
    max_inj_vol_start_idx = numpy.array( a2d_list[:][0], dtype='int' )
    max_inj_vol_final_idx = numpy.array( a2d_list[:][1], dtype='int' )
    max_inj_vol = numpy.array( a2d_list[:][2], dtype='double' )
    
    print a2d_list
    print a2d_ndarray
    print max_inj_vol_start_idx
    print max_inj_vol_final_idx
    print max_inj_vol
    print a2d_list[:]
    
    
    try:
        raise ValueError, "Hey, numpty!"
    except ValueError:
        print sys.exc_type, sys.exc_value
        
        
    myNiTuple =\
        (u'key', u'trdt_1_S_M0', u'attr', (u'dims', 1, u'sizes', (7,), u'types', (u'NI',)),
             u'data',
             (\
                (u'key', u'NAME', u'attr', (u'dims', 0, u'sizes', (), u'types', u'str'), u'data', u'trdt_1_S_M0'),
                (u'key', u'SB', u'attr', (u'dims', 0, u'sizes', (), u'types', u'int'), u'data', 1),
                (u'key', u'START_IDX', u'attr', (u'dims', 0, u'sizes', (), u'types', u'int'), u'data', 0),
                (u'key', u'END_IDX', u'attr', (u'dims', 0, u'sizes', (), u'types', u'int'), u'data', 30),
                (u'key', u'TRADE_SIZE_MIN', u'attr', (u'dims', 0, u'sizes', (), u'types', u'float'), u'data', 0.0),
                (u'key', u'TRADE_SIZE_MAX', u'attr', (u'dims', 0, u'sizes', (), u'types', u'float'), u'data', 30.0),
                (u'key', u'PRICE', u'attr', (u'dims', 0, u'sizes', (), u'types', u'float'), u'data', 21.614999999999998)))

    from gnw.named_item_parser import NamedItemParser
    from gnw.named_item import NamedItem, NamedItemAttr, NamedItemData
    
    myNi = NamedItemParser.parse(myNiTuple)
    myNiDict = myNi.get_dict()
    print str(myNiDict)
    
# ==============================================================================
#
#   Revision Control:
#
#   $Revision:: 500                     $   Revision of last commit
#   $Author:: re04179                   $   Author of last commit
#   $Date:: 2009-04-20 12:58:21 +0200 (#$   Date of last commit
#
# ==============================================================================
