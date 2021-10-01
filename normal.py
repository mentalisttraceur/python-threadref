# SPDX-License-Identifier: 0BSD
# Copyright 2019 Alexander Kozhevnikov <mentalisttraceur@gmail.com>

"""``weakref`` for threads.

Allows threads in Python to create "weak references" to themselves
that detect when the thread is no longer running, similar to how a
weak reference detects when its referent object is no longer alive.

Provides a lightweight way for one or more independent pieces of code
to register per-thread cleanup callbacks without coordination.
"""

__all__ = ('ref',)
__version__ = '1.1.2'


from threading import current_thread as _current_thread
from threading import local as _threadlocal
from weakref import finalize as _finalize
from weakref import ref as _weakref


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
        return super().__new__(cls, anchor, callback)

    def __init__(self, callback=None):
        """Initialize the weak reference. Same arguments as `__new__`."""
        super().__init__(_threadlocal.anchor, callback)

    def __call__(self):
        """Dereference the weak thread reference.

        Returns:
            threading.Thread: If the thread is still running.
            None: If the thread is no longer running.
        """
        anchor = super().__call__()
        if anchor is None:
            return None
        return anchor._thread

    def __repr__(self):
        """Represent the weak thread reference as an unambiguous string."""
        thread = self()
        if thread is None:
            return '<threadref ' + repr(id(self)) + ' dead>'
        return '<threadref ' + repr(id(self)) + ' ' + repr(thread) + '>'


class finalize(_finalize):
    """Finalizer for the current thread.

    Unlike normal finalizers, this detects when the current thread
    stops running, not when a given object is stops being alive.
    """

    __slots__ = ()

    def __init__(self, function, /, *args, **kwargs):
        """Initialize the finalizer.

        Arguments:
            function: Function (or other callable) to call
                once the current thread stops running.
            *args: Positional arguments for the function.
            **kwargs: Keyword arguments for the function.
        """
        try:
            anchor = _threadlocal.anchor
        except AttributeError:
            anchor = _threadlocal.anchor = _Object()
            anchor._thread = _current_thread()
        super().__init__(anchor, function, *args, **kwargs)

    def detach(self):
        """Detach the finalizer from the thread.

        Returns:
            tuple (threading.Thread, function, args, kwargs):
                If the thread is still running.
            None: If the thread is no longer running.
        """
        state = super().detach()
        if state is None:
            return None
        anchor, function, args, kwargs = state
        return (anchor._thread, function, args, kwargs)

    def peek(self):
        """Get the return value of calling detach without detaching.

        Returns:
            tuple (threading.Thread, function, args, kwargs):
                If the thread is still running.
            None: If the thread is no longer running.
        """
        state = super().peek()
        if state is None:
            return None
        anchor, function, args, kwargs = state
        return (anchor._thread, function, args, kwargs)

    def __repr__(self):
        """Represent the thread finalizer as an unambiguous string."""
        state = self.peek()
        if state is None:
            return '<threadfinalize ' + repr(id(self)) + ' dead>'
        thread, _, _, _ = state
        return '<threadfinalize ' + repr(id(self)) + ' ' + repr(thread) + '>'
