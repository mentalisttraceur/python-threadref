# Copyright 2019 Alexander Kozhevnikov <mentalisttraceur@gmail.com>
#
# Permission to use, copy, modify, and distribute this software for any
# purpose with or without fee is hereby granted.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
# OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.


"""``weakref`` for threads.

Allows threads in Python to create "weak references" to themselves
that detect when the thread is no longer running, similar to how a
weak reference detects when its referent object is no longer alive.

Provides a lightweight way for one or more independent pieces of code
to register per-thread cleanup callbacks without coordination.
"""


from threading import current_thread as _current_thread
from threading import local as _threadlocal
from weakref import ref as _weakref


__all__ = ('ref',)
__version__ = '1.0.1'


# We only need one global thread-local variable for this to work:
_threadlocal = _threadlocal()


# Plain `object` supports neither weak references nor custom attributes.
class _Object(object):
    __slots__ = ('__weakref__', '_thread')


class ref(_weakref):
    """Weak reference to the current thread.

    Unlike normal weak references, this detects when the current thread
    stops running, not when a given object is stops being alive.
    """

    __slots__ = ()

    def __new__(cls, callback=None):
        """Create a weak reference to the current thread.

        Arguments:
            callback (optional): Function (or other callable)
                to call once the current thread stops running.
        """
        try:
            anchor = _threadlocal.anchor
        except AttributeError:
            anchor = _threadlocal.anchor = _Object()
            anchor._thread = _current_thread()
        return super(ref, cls).__new__(cls, anchor, callback)

    def __init__(self, callback=None):
        """Initialize the weak reference. Same arguments as `__new__`."""
        super(ref, self).__init__(_threadlocal.anchor, callback)

    def __call__(self):
        """Dereference the weak thread reference.

        Returns:
            threading.Thread: If the thread is still running.
            None: If the thread is no longer running.
        """
        anchor = super(ref, self).__call__()
        if anchor is None:
            return None
        return anchor._thread

    def __repr__(self):
        """Represent the weak thread reference as an unambiguous string."""
        thread = self()
        if thread is None:
            return '<threadref ' + repr(id(self)) + ' dead>'
        return '<threadref ' + repr(id(self)) + ' ' + repr(thread) + '>'
