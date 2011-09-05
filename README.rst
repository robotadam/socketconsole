socketconsole
https://github.com/robotadam/socketconsole
(c) 2011 Adam Lowry

About
=====

socketconsole.py is just a simple library to provide stacktraces via UNIX
sockets. Handy for investigating running daemons.

Installation
============

Requires CPython 2 or 3 (`PyPy lacks sys._current_frames <https://bugs.pypy.org/issue863>`_)

::

    $ python setup.py install

Or copy the socketconsole.py file into your project.

Not compatible with gevent (won't crash; produces useless output).

Usage
=====

Daemon
------

In your daemon:

::

    import socketconsole
    # Stores socket files in $TMPDIR/$TEMP/$TMP or /tmp
    socketconsole.launch()
    # ...or specify where to store socket file
    socketconsole.launch(path='some/custom/path')

Command Line
------------

From the command line:

::

    $ # Looks in $TMPDIR/$TEMP/$TMP or /tmp
    $ socketreader
    $ # ... or specify where socket files are
    $ socketreader some/custom/path
    $ # Or you can run socketconsole.py directly
    $ python socketconsole.py some/custom/path
