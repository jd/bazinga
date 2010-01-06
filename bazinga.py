#!/usr/bin/env python

if __name__ == "__main__":
    import bazinga.util as util
    from bazinga.log import log

    util.setup_sys_path()

    try:
        util.load_config_file()
    except Exception, e:
        log.critical("Cannot load configuration file: %s" % e)
