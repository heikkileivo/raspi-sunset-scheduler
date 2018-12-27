#!/usr/bin/env python

import logging
LOG_FORMAT="%(message)s"
logger = logging.getLogger(__name__)

def main():

    logger.info("Hello, world!")


if __name__=='__main__':
    logging.basicConfig(format=LOG_FORMAT, level=logging.DEBUG)
    main()
