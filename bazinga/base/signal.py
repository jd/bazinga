"""Bazinga signal system. This is a simple extension to Louie."""

from louie import *
from louie.dispatcher import live_receivers, get_receivers, plugins, sends


def _get_all_receivers_mro(sender=Any, signal=All):
    """Get list of all receivers from global tables.

    This gets all receivers which should receive the given signal from
    sender, each receiver should be produced only once by the
    resulting generator.

    This also returns receivers matchin the sender and signal MRO.
    """
    yielded = set()
    _receivers = [
        # Get receivers that receive *this* signal from *this* sender.
        get_receivers(sender, signal),
        # Add receivers that receive *all* signals from *this* sender.
        get_receivers(sender, All),
        # Add receivers that receive *this* signal from *any* sender.
        get_receivers(Any, signal),
        # Add receivers that receive *all* signals from *any* sender.
        get_receivers(Any, All) ]

    for cls in sender.__class__.__mro__:
        _receivers.append(get_receivers(cls, signal))

    for cls in signal.__class__.__mro__:
        _receivers.append(get_receivers(sender, cls))

    for receivers in _receivers:
        for receiver in receivers:
            if receiver: # filter out dead instance-method weakrefs
                try:
                    if not receiver in yielded:
                        yielded.add(receiver)
                        yield receiver
                except TypeError:
                    # dead weakrefs raise TypeError on hash...
                    pass


def emit(signal=signal.All, sender=sender.Anonymous, *arguments, **named):
    """Emit a signal. This is the same as send, except that it also emit the
    signal on object classes, following MRO."""
    # Call each receiver with whatever arguments it can accept.
    # Return a list of tuple pairs [(receiver, response), ... ].
    responses = []
    for receiver in live_receivers(_get_all_receivers_mro(sender, signal)):
        # Wrap receiver using installed plugins.
        original = receiver
        for plugin in plugins:
            receiver = plugin.wrap_receiver(receiver)
        response = robustapply.robust_apply(
            receiver, original,
            signal=signal,
            sender=sender,
            *arguments,
            **named
            )
        responses.append((receiver, response))
    # Update stats.
    if __debug__:
        global sends
        sends += 1
    return responses


def connected(signal=signal.All, sender=sender.Any, weak=True):
    """Return a decorator function that will connect
    the underlying function to an event."""

    def connect_func(func):
        connect(func, signal, sender)
        return func

    return connect_func
