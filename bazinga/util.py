from xdg import BaseDirectory

loaded_config_file = None

def get_config_file():

    """Load configuration file."""

    return BaseDirectory.load_first_config("bazinga", "rc.py")


def load_config_file():

    configfile = get_config_file()

    if configfile:
        try:
            execfile(configfile)
        except:
            raise Exception("error executing configuration file")
        else:
            loaded_config_file = configfile
    else:
        raise Exception("configuration file not found")


def setup_sys_path():

    """Setup sys.path to use XDG config dir"""

    import sys, os
    for directory in BaseDirectory.xdg_config_dirs:
        sys.path.insert(0, os.path.join(directory, "bazinga"))
