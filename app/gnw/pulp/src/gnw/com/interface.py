# ==============================================================================
#
#   package         :   GasNetWorks (gnw) Python/pulp fuelled LP/MIP modeller 
#   author          :   Marc Roth (re04179)
#   version         :   $Id: interface.py 9768 2010-09-22 20:07:23Z re04179 $
#   heading         :   $HeadURL: http://subversion.rwe.com/svn/s_and_v_projects/GasNetworks/trunk/app/gnw/pulp/src/gnw/com/interface.py $
#
#   Description     :   COM interface sub-package
#
#   Creation Date   :   12Mar2009
#
#   Copyright       :   RWE Supply and Trading GmbH
#
# ==============================================================================
"""
gnw.com: Used to register and unregister COM objects listed in variable
L{__servers__}. For further help, execute:
    - > python interface.py --help
"""
from gnw.com.network import COM_Network
from gnw.com.product import COM_Product
from gnw.com.storage import COM_Storage
from gnw.com.tranche import COM_Tranche
from gnw.com.supplier import COM_Supplier
from gnw.com.dispatch_product import COM_DispatchProduct
from gnw.com.firm_profile import COM_FirmProfile
from gnw.com.market import COM_Market


__servers__ = ( COM_Network,
                COM_Product,
                COM_Storage,
                COM_Tranche,
                COM_Supplier,
                COM_DispatchProduct,
                COM_FirmProfile,
                COM_Market ) 


def install():
    """Used in post_install.py script in ./src/gnw.egg-info folder"""
    import os
    if os.name == 'nt': 
        import win32com.server.register
        win32com.server.register.RegisterClasses( *__servers__ )
        
def install_debug():
    """Used in regcom.py script"""
    import os
    if os.name == 'nt':
        import win32com.server.register
        win32com.server.register.UseCommandLine( *__servers__ )

def install_debug():
    """Used in regcom.py script"""
    import os
    if os.name == 'nt':
        import win32com.server.register
        win32com.server.register.UseCommandLine( *__servers__ )

def remove():
    """Used in pre_uninstall.py script in ./src/gnw.egg-info folder"""
    import os
    if os.name == 'nt':
        import win32com.server.register
        win32com.server.register.UnregisterClasses( *__servers__ )


if __name__ == "__main__" :
    import sys
    import optparse
    import win32com.server.register

    if len( sys.argv ) > 1:
        # In case we are called
        # as a post install script
        # from the python distutils
        # installer:
        # On installation it will call the script with '-install' argument
        # On de-installation it will call the script with '-remove' argument'
        # (note the single leading dash character; optparse does not
        # accept long format options with only a single dash character)
        for idx in xrange(1, len( sys.argv ) ):
            if sys.argv[idx] == '-install':
                sys.argv[idx] = '--install'
            if sys.argv[idx] == '-remove':
                sys.argv[idx] = '--remove'

    parser = optparse.OptionParser()
    parser.add_option("-i", "--install",
                      dest="register", action="store_true", default=True,
                      help="register COM servers [default]")
    parser.add_option("-r", "--remove",
                      dest="register", action="store_false",
                      help="de-register COM servers")
    parser.add_option("-v", "--verbose",
                      dest="verbose", action="store_true", default=True,
                      help="being verbose [default]")
    parser.add_option("-s", "--silent",
                      dest="verbose", action="store_false",
                      help="suppress console output")
    parser.add_option("-l", "--list",
                      dest="listing", action="store_true", default=False,
                      help="list names of servers and exit")
    parser.add_option("--debug",
                      dest="use_command_line", action="store_true", default=False,
                      help="register servers using 'win32com.server.register.UseCommandLine' "
                      "causing the servers being registered with '--debug' flag set")
    (options, args) = parser.parse_args()

    if options.listing:
        for srvr in __servers__:
            print srvr
    else:
        if options.use_command_line:
            if options.verbose:
                print "Registering COM server in debug mode..."
            win32com.server.register.UseCommandLine( *__servers__ )
        else:
            if options.register:
                if options.verbose:
                    print "Registering COM server..."
                win32com.server.register.RegisterClasses( *__servers__ )
            else:
                if options.verbose:
                    print "Unregistering COM server..."
                win32com.server.register.UnregisterClasses( *__servers__ )

# ==============================================================================
#
#   Revision Control:
#
#   $Revision:: 9768                    $   Revision of last commit
#   $Author:: re04179                   $   Author of last commit
#   $Date:: 2010-09-22 22:07:23 +0200 (#$   Date of last commit
#
# ==============================================================================
