#! /usr/bin/env python3
# -*- coding: utf-8 -*-
import optparse
import os
import time

import yaml
from rspub.core.rs_enum import Strategy

from resyncserver.elastic.elastic_rs import ElasticResourceSync
from resyncserver.elastic.elastic_rs_paras import ElasticRsParameters

RESOURCE_TYPE = "resource"


class ElasticGenerator(object):

    def __init__(self, config):
        self.config = config

    def generate(self):
        rs = ElasticResourceSync(**self.config.__dict__)
        rs.execute()
        return 0

    def generate_resourcelist(self):
        self.config.strategy = Strategy.resourcelist.value
        return self.generate()

    def generate_new_changelist(self):
        self.config.strategy = Strategy.new_changelist.value
        return self.generate()


def main():
    parser = optparse.OptionParser()
    parser.add_option('--config-file', '-c',
                      help="the source configuration file")

    # Parse command line arguments
    (args, clargs) = parser.parse_args()

    if len(clargs) > 0:
        parser.print_help()
        return
    if args.config_file is None:
        parser.print_help()
        return

    config = yaml.load(open(args.config_file, 'r'))['executor']

    if not os.path.exists(config['description_dir']):
        os.makedirs(config['description_dir'])

    rs_params = ElasticRsParameters(**config)
    start = time.clock()

    gener = ElasticGenerator(rs_params)
    gener.generate_resourcelist()

    elapsed_time = time.clock() - start
    print("Elapsed time:", elapsed_time)
    print("Published simple resourcelist at", rs_params.last_execution)

    # todo
    # ch_params = RsParameters(**params)
    # gener = ElasticGenerator(rs_params, INDEX, RESOURCE_TYPE)
    # gener.generate_new_changelist()
    # print("Published capabilitylist at", ch_params.last_execution)


if __name__ == '__main__':
    main()

