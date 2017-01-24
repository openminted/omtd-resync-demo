#!/usr/bin/env python
# encoding: utf-8
"""

ResourceSync tool for exposing a changing Web data source.

Created by Giorgio Basile on 09-01-2017
"""
import optparse
import os

import yaml
import logging
import logging.config

from resyncserver._version import __version__
from resyncserver.http_interface import HTTPInterface
from resyncserver.source import Source

DEFAULT_LOG_FILE = 'config/logging.yaml'


def main():

    # Define server options
    parser = optparse.OptionParser(description="ResourceSync Server",
                                   usage='usage: %prog [options]  (-h for help)',
                                   version='%prog '+__version__)
    parser.add_option('--config-file', '-c',
                      help="the source configuration file")
    parser.add_option('--log-config', '-l',
                      default=DEFAULT_LOG_FILE,
                      help="the logging configuration file")
    parser.add_option('--port', '-p', type=int,
                      default=8888,
                      help="the HTTP interface port that the server will run on")

    # Parse command line arguments
    (args, clargs) = parser.parse_args()

    if len(clargs) > 0:
        parser.print_help()
        return
    if args.config_file is None:
        parser.print_help()
        return

    logconfig = yaml.load(open(args.log_config, 'r'))
    logging.config.dictConfig(logconfig)

    config = yaml.load(open(args.config_file, 'r'))['source']

    source = Source(config, args.port)
    source.bootstrap()
    r = os.path.abspath(config['publisher_configs'][0])

    http_interface = HTTPInterface(source)
    try:
        pass
        print("ResourceSync server started on port " + str(args.port))
        http_interface.run()
    except KeyboardInterrupt:
        print("Exiting gracefully...")
    finally:
        http_interface.stop()

if __name__ == '__main__':
    main()
