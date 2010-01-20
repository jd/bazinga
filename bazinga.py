#!/usr/bin/env python

if __name__ == "__main__":
    import bazinga.base as base
    from bazinga.log import log

    base.setup_sys_path()

    try:
        base.load_config_file()
    except Exception, e:
        log.critical("Cannot load configuration file: %s" % e)
