#!/usr/bin/env python
import logging
import os, sys
import argparse
import shutil
from datetime import datetime
from calc import Suncalc, MODES

LOG_FORMAT="%(message)s"

logger = logging.getLogger(__name__)

def init():
    """
    Create settings module if it does not exist.
    """
    path = os.path.join(sys.path[0], 'settings.py')
    if os.path.isfile(path) == False:
        template = os.path.join(sys.path[0], 'sample_settings.py')
        shutil.copyfile(template, path)
        print("Created settings.py module from sample.")

def run_commands(args):
    """
    Output or execute commands as specified in settings.
    """
    init()
    from settings import LATITUDE, LONGITUDE
    from settings import commands, MODE
    s = Suncalc(LATITUDE, LONGITUDE, MODE)

    local_dt = datetime.now() 
    value = s.local_value(local_dt)
    for c in commands(value):
        if args.execute: 
            os.system(c)
        else:
            print(c)

def show_time(args):
    """
    Output fime for selected event.
    """
    init()
    from settings import LATITUDE, LONGITUDE
    s = Suncalc(LATITUDE, LONGITUDE, args.event)
    local_dt = datetime.now()
    value = s.local_value(local_dt)

    print("Local {} is at {}".format(args.event, value))

def main():
    parser = argparse.ArgumentParser("Sunset Calculator")
    subparsers = parser.add_subparsers(help="Action to perfom.")

    # Define parser for show-time action
    subparser = subparsers.add_parser("show-time", 
        help="Show time for specifi event.")
    subparser.add_argument('--event', required=True, type=str, choices=MODES,
        help="Defines event to be observed.")
    subparser.set_defaults(func=show_time)

    # Define parser for run-commands action
    subparser = subparsers.add_parser("run-commands", 
        help="Run commands specified in settings.")
    subparser.set_defaults(func=run_commands)
    subparser.add_argument('--execute', type=bool, 
        default=False, help="If set to True, execute commands using os.system.")
    args = parser.parse_args()

    if hasattr(args, 'func') == False:
        parser.print_help()
        return
    try:
        args.func(args)
    except:
        e = sys.exc_info()
        logger.error("Operation failed: {0}".format(e[1]))

    
if __name__=='__main__':
    logging.basicConfig(format=LOG_FORMAT, level=logging.DEBUG)
    main()
