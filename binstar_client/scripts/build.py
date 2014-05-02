'''
Binstar Build command

Initialize the build directory:

    binstar-build init
    
This will create a default .binstar.yml file in the current directory
  
Submit a build:

    binstar-build submit
    
Tail the output of a build untill it is complete:

    binstar-build tail user/package 1.0
    
'''
from argparse import ArgumentParser, RawDescriptionHelpFormatter
from binstar_client.build_commands import sub_commands
from binstar_client.errors import BinstarError, ShowHelp, Unauthorized
from binstar_client.commands.login import interactive_login
from binstar_client import __version__ as version
import logging
from binstar_client.utils import USER_LOGDIR
from os.path import join, exists
from os import makedirs
from logging.handlers import RotatingFileHandler
from binstar_client.utils.handlers import MyStreamHandler

logger = logging.getLogger('binstar')

def setup_logging(args):

    if not exists(USER_LOGDIR): makedirs(USER_LOGDIR)

    logger = logging.getLogger('binstar')
    logger.setLevel(logging.DEBUG)

    error_logfile = join(USER_LOGDIR, 'cli.log')
    hndlr = RotatingFileHandler(error_logfile, maxBytes=10 * (1024 ** 2), backupCount=5,)
    hndlr.setLevel(logging.INFO)
    logger.addHandler(hndlr)

    shndlr = MyStreamHandler()
    shndlr.setLevel(args.log_level)
    logger.addHandler(shndlr)

def main():



    parser = ArgumentParser(description=__doc__,
                            formatter_class=RawDescriptionHelpFormatter)
    parser.add_argument('--show-traceback', action='store_true')
    parser.add_argument('-t', '--token')
    parser.add_argument('-v', '--verbose',
                        action='store_const', help='print debug information ot the console',
                        dest='log_level',
                        default=logging.INFO, const=logging.DEBUG)
    parser.add_argument('-q', '--quiet',
                        action='store_const', help='Only show warnings or errors the console',
                        dest='log_level', const=logging.WARNING)
    parser.add_argument('-V', '--version', action='version',
                        version="%%(prog)s Command line client (version %s)" % (version,))
    subparsers = parser.add_subparsers(help='commands')

    for command in sub_commands():
        command.add_parser(subparsers)

    args = parser.parse_args()

    setup_logging(args)
    try:
        try:
            return args.main(args)
        except Unauthorized as err:
            if not args.token:
                print 'The action you are performing requires authentication, please sign in:'
                interactive_login()
                return args.main(args)
            else:
                raise

    except ShowHelp as err:
        args.sub_parser.print_help()
        raise SystemExit(1)
    except (BinstarError, KeyboardInterrupt) as err:
        if args.show_traceback:
            raise
        logger.exception(err.message)
        raise SystemExit(1)
