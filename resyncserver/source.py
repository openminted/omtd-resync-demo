#!/usr/bin/env python
# encoding: utf-8
"""
source.py: A source holds a set of resources and changes over time.

Created by Giorgio Basile on 09-01-2017.
"""

import logging
import os
import pprint
import random
import time
from concurrent.futures import ThreadPoolExecutor

from tornado import gen

from resyncserver.elastic.elastic_generator import ElasticGenerator
from resyncserver.elastic.elastic_rs_paras import ElasticRsParameters
from resyncserver.observer import Observable


class DynamicResourceListBuilder(object):
    """Generates an resource_list snapshot from a source."""

    def __init__(self, source):
        """Initialize the DynamicResourceListBuilder."""
        self.source = source
        self.config = self.source.publish_configs
        self.logger = logging.getLogger('resource_list_builder')
        self.executor = self.source.executor

    def bootstrap(self):
        """Bootstrapping procedures implemented in subclasses."""
        # todo implement a policy for resourcelist regeneration, this will not triggered in the source bootstrap
        #self.generate()
        pass

    @gen.coroutine
    def generate(self, config):
        """Generate a resource_list (snapshot from the source)."""
        then = time.time()
        self.new_resource_list()
        now = time.time()
        self.logger.info("Generated resource_list: %f" % (now - then))

    @gen.coroutine
    def new_resource_list(self):
        f = yield self.executor.submit(self.res_gen)
        print(str(f))

    def res_gen(self):
        rs_params = ElasticRsParameters(**self.source.config)
        gener = ElasticGenerator(rs_params)
        return gener.generate_resourcelist()


class Source(Observable):
    """A source contains a list of resources and changes over time."""

    RESOURCE_PATH = "/resources"  # to append to base_uri
    STATIC_FILE_PATH = os.path.join(os.path.dirname(__file__), "static")

    def __init__(self, config, port):
        """Initalize the source."""
        super(Source, self).__init__()
        self.logger = logging.getLogger('source')
        self.config = config
        self.logger.info("Source config: %s " % self.config)
        self.port = port
        self.max_res_id = 1
        self._repository = {}  # {basename, {timestamp, length}}
        self.resource_list_builder = None  # builder implementation
        self.changememory = None  # change memory implementation
        self.no_events = 0
        self._executor = ThreadPoolExecutor(max_workers=4)
        self.publish_configs = self.config['publisher_configs']

        self.add_resource_list_builder(DynamicResourceListBuilder(self))

    @property
    def executor(self):
        return self._executor

    # Source capabilities

    def add_resource_list_builder(self, resource_list_builder):
        """Add a resource_list builder implementation."""
        self.resource_list_builder = resource_list_builder

    @property
    def has_resource_list_builder(self):
        """Return True if the Source has an resource_list builder."""
        return bool(self.resource_list_builder is not None)

    def add_changememory(self, changememory):
        """Add a changememory implementation."""
        self.changememory = changememory

    @property
    def has_changememory(self):
        """Return True if a source maintains a change memory."""
        return bool(self.changememory is not None)

    # Bootstrap Source

    def bootstrap(self):
        """Bootstrap the source with a set of resources."""
        self.logger.info("Bootstrapping source...")
        if self.has_changememory:
            self.changememory.bootstrap()
        if self.has_resource_list_builder:
            # todo do it for all of them
            self.resource_list_builder.bootstrap()
        self._log_stats()

    # Source data accessors

    @property
    def describedby_uri(self):
        """Description of Source"""
        return '/'

    @property
    def source_description_uri(self):
        """URI of Source Description document.

        Will use standard pattern for well-known URI unless
        an explicit configuration is given.
        """
        if 'source_description_uri' in self.config:
            return self.config['source_description_uri']
        return '.well-known/resourcesync'

    @property
    def resource_count(self):
        """The number of resources in the source's repository."""
        return len(self._repository)

    @property
    def random_resource(self):
        """Return a single random resource."""
        rand_res = self.random_resources()
        if len(rand_res) == 1:
            return rand_res[0]
        else:
            return None

    def resource(self, basename):
        """Create and return a resource object."""
        return None

    def random_resources(self, number=1):
        """Return a random set of resources, at most all resources."""
        if number > len(self._repository):
            number = len(self._repository)
        rand_basenames = random.sample(self._repository.keys(), number)
        return [self.resource(basename) for basename in rand_basenames]

    def _log_stats(self):
        """Output current source statistics via the logger."""
        stats = {
            'no_resources': self.resource_count,
            'no_events': self.no_events
        }
        self.logger.info("Source stats: %s" % stats)

    def __str__(self):
        """Print out the source's resources."""
        return pprint.pformat(self._repository)


