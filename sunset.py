#!/usr/bin/env python
import logging
import os, sys
import argparse
import shutil
from datetime import datetime
from calc import Suncalc, EVENTS
from glob import glob

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
    from settings import commands, EVENT
    s = Suncalc(LATITUDE, LONGITUDE, EVENT)

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

def collect_images(args):
    """
    Collect images with same index number to target directory.
    Order collected files by date created and create symbolic link
    for each file using numeric counter as filename.
    """
    from settings import TARGET_DIRECTORY as source_dir # sic!
    if os.path.isdir(source_dir):
        if os.path.isdir(args.target) == False:
            os.makedirs(args.target)
        if args.purge:
            # Remove old files in target directory
            g = glob(os.path.join(args.target, "*"))
            count = len(g)
            if count > 0: 
                if args.silent == False:
                    print("All files in target directory {} will be deleted.")
                    print("Do you want to continue? (y/n)")
                    if input().lower() != 'y': 
                        print("Operation cancelled.")
                        return
                for file in g:
                    os.remove(file)
                print("Successfully created {} symlinks to {}.".format(count, args.target))
            else:
                print("No files found to be processed.")

        pattern = os.path.join(source_dir, args.subdir, "*{:+d}.jpg".format(args.offset))
        files = sorted(glob(pattern), key=os.path.getmtime)
        for index, path in enumerate(files):
            os.symlink(path, os.path.join(args.target, "{:d}.jpg".format(index)))
            
    else:
        print("Source directory defined in settings does not exist.".format(TARGET_DIRECTORY))

def main():
    parser = argparse.ArgumentParser("Sunset Calculator")
    subparsers = parser.add_subparsers(help="Action to perfom.")

    # Define parser for show-time action
    subparser = subparsers.add_parser("show-time", 
        help="Show time for specific event.")
    subparser.add_argument('--event', required=True, type=str, choices=EVENTS,
        help="Defines event to be observed.")
    subparser.set_defaults(func=show_time)

    # Define parser for run-commands action
    subparser = subparsers.add_parser("run-commands", 
        help="Run commands specified in settings.")
    subparser.set_defaults(func=run_commands)
    subparser.add_argument('--execute', type=bool, 
        default=False, help="If set to True, execute commands using os.system.")

    # Define parser for collect-images action
    subparser = subparsers.add_parser("collect-images", 
        help="Collect images for creating time-lapse video.")
    subparser.set_defaults(func=collect_images)
    subparser.add_argument('--offset', type=int, required=True, 
        help="Index of images to be collected.")
    subparser.add_argument('--target', type=str, required=True,
        help="Target path for images.")
    subparser.add_argument('--subdir', type=str, required=False, default='', 
        help="Sub-directory to look for images.")
    subparser.add_argument('--purge', type=bool, default=False, 
        help="If set to True, remove old files before proceeding.")
    subparser.add_argument('--silent', type=bool, default=False, 
        help="If set to True, do not ask for confirmation.")

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
