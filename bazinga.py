#!/usr/bin/env python

if __name__ == "__main__":
    import bazinga.core.util as util
    from bazinga.core import log
    import logging

    util.setup_sys_path()

    try:
        util.load_config_file()
    except Exception, e:
        log.critical("Cannot load configuration file: %s" % e)
