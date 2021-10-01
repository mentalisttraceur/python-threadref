``weakref`` for Threads
=======================

Allows threads in Python to create "weak references" to themselves
that detect when the thread is no longer running, similar to how a
weak reference detects when its referent object is no longer alive.

Provides a lightweight way for one or more independent pieces of code
to register per-thread cleanup callbacks without coordination.


Versioning
----------

This library's version numbers follow the `SemVer 2.0.0
specification <https://semver.org/spec/v2.0.0.html>`_.


Installation
------------

::

    pip install threadref


Usage
-----

Import:

.. code:: python

    import threadref


``ref``
~~~~~~~

Create a reference to the current thread, with a
callback that will fire when the thread exits:

.. code:: python

    reference = threadref.ref(lambda reference: ...)

``threadref.ref`` mirrors ``weakref.ref``, except that:

1. It references the thread that constructed it
   instead of taking a referent argument.

2. It starts returning ``None`` instead of the ``threading.Thread``
   object for its thread once the thread stops running, not once
   that object stops being alive.

So just like ``weakref.ref``, ``threadref.ref`` instances
must still be alive when their referent thread stops
running, or their callback will not be called.


``finalize``
~~~~~~~~~~~~

Create a finalizer for the current thread, which
will be called when the thread exits:

.. code:: python

    finalizer = threadref.finalize(function, *args, **kwargs)

``threadref.finalize`` mirrors ``weakref.finalize``, except that:

1. It references the thread that constructed it
   instead of taking a referent argument.

2. In all cases where ``weakref.finalize`` returns the tuple
   ``(object, function, args, kwargs)``, it returns the tuple
   ``(thread, function, args, kwargs)`` instead.

3. It starts returning ``None`` once the thread stops running.

The finalizer remains alive on its own as long as it needs to,
so this is a simpler and nicer interface in the typical case
of registering cleanup functions.


Portability
-----------

Internally, ``threadref`` is just a weak reference to a thread
local variable, and this trick seems to only work on CPython
implementations with the C implementation of ``threading.local``.
