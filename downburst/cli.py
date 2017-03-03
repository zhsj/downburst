import argparse
import logging
import pkg_resources
import sys

from . import exc


log = logging.getLogger(__name__)


def parse_args():
    parser = argparse.ArgumentParser(
        description='Create an Ubuntu Cloud image vm',
        )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true', default=None,
        help='be more verbose',
        )
    parser.add_argument(
        '-l', '--logfile',
        help='additional logfile (same as stderr log)',
        )
    parser.add_argument(
        '-c', '--connect',
        metavar='URI',
        help='libvirt URI to connect to',
        )
    sub = parser.add_subparsers(
        title='commands',
        metavar='COMMAND',
        help='description',
        )
    for ep in pkg_resources.iter_entry_points('downburst.cli'):
        fn = ep.load()
        p = sub.add_parser(ep.name, help=fn.__doc__)
        # ugly kludge but i really want to have a nice way to access
        # the program name, with subcommand, later
        p.set_defaults(prog=p.prog)
        fn(p)
    parser.set_defaults(
        # we want to hold on to this, for later
        prog=parser.prog,
        connect='qemu:///system',
        )
    args = parser.parse_args()
    return args


def main():
    args = parse_args()

    # turn off urllib3 connectionpool logging
    logging.getLogger('requests.packages.urllib3.connectionpool').setLevel(
        logging.WARN)
    logging.getLogger('urllib3.connectionpool').setLevel(logging.WARN)

    loglevel = logging.INFO
    if args.verbose:
        loglevel = logging.DEBUG

    logging.basicConfig(
        level=loglevel,
        )

    if args.logfile:
        logger = logging.getLogger()
        logger.addHandler(logging.FileHandler(filename=args.logfile))

    try:
        return args.func(args)
    except exc.DownburstError as e:
        print >>sys.stderr, '{prog}: {msg}'.format(
            prog=args.prog,
            msg=e,
            )
        sys.exit(1)
