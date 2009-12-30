from xdg import BaseDirectory

def get_config_file():

    """Load configuration file."""

    return BaseDirectory.load_first_config("bazinga", "rc.py")

def setup_sys_path():

    """Setup sys.path to use XDG config dir"""

    import sys, os
    for directory in BaseDirectory.xdg_config_dirs:
        sys.path.insert(0, os.path.join(directory, "bazinga"))
