#!/usr/bin/env python3


class ConfServerApp:
    """Class to be implemented by plugins."""

    name = None
    plugin_type = None
    path_prefix = None
    app = None
    sub_api = None
    routes = None
