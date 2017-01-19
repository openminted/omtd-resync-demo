#!/usr/bin/env python
# encoding: utf-8
"""
http_interface.py: The source's HTTP Web interface.

Runs on the non-blocking Tornado web server (http://www.tornadoweb.org/)

Created by Bernhard Haslhofer on 2012-04-24.
Edited by Giorgio Basile  on 2016-12-12.
"""
import mimetypes
import threading
import os.path
import logging
from datetime import datetime

import tornado.httpserver
import tornado.ioloop
import tornado.web

from resyncserver.source import Source


class HTTPInterface(object):
    """The repository's HTTP interface.

    To make sure it doesn't interrupt
    the simulation, it runs in a separate thread.

    http://stackoverflow.com/questions/323972/
        is-there-any-way-to-kill-a-thread-in-python (Stoppable Threads)

    http://www.slideshare.net/juokaz/
        restful-web-services-with-python-dynamic-languages-conference
    """

    def __init__(self, source):
        """Initialize HTTP interface with default settings and handlers."""
        super(HTTPInterface, self).__init__()
        self.logger = logging.getLogger('http')
        self.source = source
        self._stop = threading.Event()
        self.port = source.port
        self.settings = dict(
            title=u"ResourceSync Server",
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=Source.STATIC_FILE_PATH,
            source_path=source.config['resource_dir'],
            autoescape=None,
        )
        self.handlers = [
            (r"/", HomeHandler, dict(source=self.source)),
            (r"/(.*)", ResourceHandler,
             dict(source=self.source)),
            (r"/(favicon\.ico)", tornado.web.StaticFileHandler,
             dict(path=self.settings['static_path'])),
        ]

    def run(self):
        """Run server."""

        self.logger.info("Starting up HTTP Interface on port %i" % (self.port))
        application = tornado.web.Application(
            handlers=self.handlers,
            debug=True,
            **self.settings)
        self.http_server = tornado.httpserver.HTTPServer(application)
        self.http_server.listen(self.port)
        tornado.ioloop.IOLoop.instance().start()

    def stop(self):
        """Stop server."""
        self.logger.info("Stopping HTTP Interface")
        tornado.ioloop.IOLoop.instance().stop()
        self._stop.set()

    def stopped(self):
        """True if server is stopped."""
        return self._stop.isSet()


class BaseRequestHandler(tornado.web.RequestHandler):
    """Handler for source."""

    SUPPORTED_METHODS = ("GET")

    def initialize(self, source):
        """Initialize with supplied source."""
        self.source = source


class HomeHandler(BaseRequestHandler):
    """Root URI handler."""

    def get(self):
        """Implement GET for homepage."""
        self.render("home.html",
                    resource_count=self.source.resource_count,
                    source=self.source)


class ResourcesHandler(BaseRequestHandler):
    """Resources subset selection handler."""

    def get(self):
        """Implement GET for resources."""
        rand_res = sorted(self.source.random_resources(100),
                          key=lambda res: res.uri)
        self.render("resource.index.html",
                    resources=rand_res,
                    source=self.source)


class ResourceHandler(BaseRequestHandler):
    """Resource handler."""

    def get(self, base_url: str):
        print("Received request at: " + base_url)
        """Implement GET for resource."""
        file_path = self.settings["source_path"] + "/" + base_url

        if not os.path.isfile(file_path):
            self.send_error(404)
        else:
            payload = open(file_path).read()

            if file_path.endswith(".well-known/resourcesync"):
                self.set_header("Content-Type", "application/xml")
            else:
                (type, enc) = mimetypes.guess_type(file_path)
                self.set_header("Content-Type", type)
                if enc is not None:
                    self.set_header("Content-Encoding", enc)

            self.set_header("Content-Length", os.path.getsize(file_path))
            self.set_header("Last-Modified", datetime.fromtimestamp(os.path.getmtime(file_path)))
            self.write(payload)
