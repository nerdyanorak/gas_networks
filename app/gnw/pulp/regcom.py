# ==============================================================================
#
#   Package         :   Gas NetWork (GNW) Python/PuLP fuelled LP/MIP
#                       modeller  
#   Author          :   Marc Roth (re04179)
#
#   Version         :   $Id:$
#   Header          :   $URL:$
#
#   Description     :   Package file
#
#   Creation Date   :   21Sep2010
#
#   Copyright       :   RWE Supply and Trading GmbH
#
# ==============================================================================
""" Used to register and unregister COM objects listed in variable
L{gnw.com.interface.__servers__}. For further help, execute:
    - > python regcom.py --help
"""
if __name__ == "__main__" :
    import sys
    import optparse

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
        from gnw.com.interface import __servers__
        for srvr in __servers__:
            print srvr
    else:
        if options.use_command_line:
            if options.verbose:
                print "Registering COM server in debug mode..."
            from gnw.com.interface import install_debug
            install_debug()
        else:
            if options.register:
                if options.verbose:
                    print "Registering COM server..."
                from gnw.com.interface import install
                install()
            else:
                if options.verbose:
                    print "Unregistering COM server..."
                from gnw.com.interface import remove
                remove()

# ==============================================================================
#
#   Revision Control:
#
#   $Revision:: 8778                                 $   Revision of last commit
#   $Author:: re04179                                $     Author of last commit
#   $Date:: 2010-07-30 18:04:23 +0200 (Fri, 30 Jul 2#$       Date of last commit
#
# ==============================================================================
