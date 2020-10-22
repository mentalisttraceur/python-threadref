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

Create a reference to the current thread, with a
callback that will fire when the thread exits:

.. code:: python

    ref = threadref.ref(lambda ref: ...)

``threadref.ref`` mirrors ``weakref.ref``, except that:

1. It references the thread that constructed it
   instead of taking a referent argument.

2. It starts returning ``None`` instead of the ``threading.Thread``
   object for its thread once the thread stops running, not once
   that object stops being alive.

So all ``weakref.ref`` caveats apply. In particular, ``threadref.ref``
instances must still be alive when their referent thread stops
running, or their callback will not be called.


Portability
-----------

Internally, ``threadref`` is just a weak reference to a thread
local variable, and this trick seems to only works on CPython
implementations with the C implementation of ``threading.local``.
