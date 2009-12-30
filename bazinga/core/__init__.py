import logging

log = logging.getLogger('bazinga')
_channel = logging.StreamHandler()
_channel.setFormatter(logging.Formatter("%(name)s: %(levelname)s: %(message)s"))
_channel.setLevel(logging.DEBUG)
log.addHandler(_channel)
del(_channel)
