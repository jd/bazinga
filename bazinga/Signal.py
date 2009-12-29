from louie import *

# Copy louie send function
send_simple = send

# Override send function from louie to send to class and parent classes
def send(signal=signal.All, sender=sender.Anonymous, *arguments, **named):
    ret = []
    for s in [ sender ] + list(sender.__class__.__mro__):
        ret += send_simple(signal=signal, sender=s, *arguments, **named)
    return ret
