Logdecorator
============

|Downloads|

Move logging code out of your business logic with python decorators.

Logging is a nice tool in your toolbox for tracing bugs and getting a
better sense how your application is working in production. But if you
are like me, you often omit logging code, so it will not hide business
logic or feature your code with complexity.

Fortunately pythons decorator now came to our rescue and provides us
with a nice library to add logging to our code without stealing
readability and understandability.

If you want to know more about the intentions behind logdecorator check
out my `blog
post <https://www.sighalt.de/remove-visual-noise-of-logging-code-by-using-python-decorators.html>`__.

Update: logdecorator==2.0
-------------------------

Thanks to all dependants :) I just released a new version of
logdecorator (2.0). You can read the changes at my
`blog <https://www.sighalt.de/a-new-logdecorator-version-is-available-o.html>`__.

Installation
------------

Installation is as easy as it can get:

.. code:: bash

    $ pip install logdecorator

How to use it
-------------

Imagine a function ``download`` with no arguments and some download code
in it.

.. code:: python

    def download():
        # some download code
        pass

    if __name__ == "__main__":
        download()
        

Say you are going to launch your new tool but want to add some logging
before releasing the kraken. Your code will probably look something like
the following:

.. code:: python

    import logging
    from .exceptions import MyException1, MyException2

    logger = logging.getLogger(__name__)


    def download():
        logger.debug("Start downloading")
        # some download code
        logger.debug("Downloading finished successfully")


    if __name__ == "__main__":
        try:
            download()
        except (MyException1, MyException2):
            logger.error("Error on downloading")
            raise

You just added at least a couple lines of code which are eventually
stumbling in your way when you are trying to understand your business
logic to find a bug. But what's even worse is, that you added an
additional indentation (try:... except: ...) just for the sake of
logging.

With logdecorator you can leave your code nearly as it was and reach the
same goals.

.. code:: python

    import logging
    from logdecorator import log_on_start, log_on_end, log_on_error
    from .exceptions import MyException1, MyException2


    @log_on_start(logging.DEBUG, "Start downloading")
    @log_on_error(logging.ERROR, "Error on downloading",
                  on_exceptions=(MyException1, MyException2),
                  reraise=True)
    @log_on_end(logging.DEBUG, "Downloading finished successfully")
    def download():
        # some download code


    if __name__ == "__main__":
        download()

Maybe the improvement to the previous snippet does not seem great for
you but if you actually fill in business logic into
``# some download code`` it should become obvious :)

What logdecorator can do for you
--------------------------------

Decorators
~~~~~~~~~~

logdecorator provides four different built-in decorators:

-  log\_on\_start
-  log\_on\_end
-  log\_on\_error
-  log\_exception

whose behaviour corresponds to their names.

Use variables in messages
~~~~~~~~~~~~~~~~~~~~~~~~~

The message, given to the decorator, is treated as a python format
string which takes the functions arguments as format arguments.

Sticking to the previous example one could write:

.. code:: python


    import logging
    from logdecorator import log_on_start
    from .exceptions import MyException1, MyException2


    @log_on_start(logging.DEBUG, "Start downloading '{url:s}'")
    def download(url):
        # some download code


    if __name__ == "__main__":
        download("http://my.file.com/file.bin")

Which results in the message
``Start downloading 'http://my.file.com/file.bin'`` gets logged.

Arguments
~~~~~~~~~

log\_on\_start
^^^^^^^^^^^^^^

**log\_level** > The log level at which the message should be send

**message** > The message to log

**logger** *(optional)* > An alternative logger object. If no logger is
given logdecorator creates a > logger object with the name of the module
the decorated function is in > (``decorated_function.__module__``) > >
Default: Creates a new logger with the name
``decorated_function.__module__``

log\_on\_end
^^^^^^^^^^^^

**log\_level** > The log level at which the message should be send

**message** > The message to log

**logger** *(optional)* > An alternative logger object. If no logger is
given logdecorator creates a > logger object with the name of the module
the decorated function is in > (``decorated_function.__module__``) > >
Default: Creates a new logger with the name
``decorated_function.__module__``

**result\_format\_variable** *(optional)* > The variable name one can
use in the message to reference the result of the > decorated function >
e.g. @log\_on\_end(DEBUG, "Result was: {result!r}") > > Default:
"result"

log\_on\_error
^^^^^^^^^^^^^^

**log\_level** > The log level at which the message should be send

**message** > The message to log

**logger** *(optional)* > An alternative logger object. If no logger is
given logdecorator creates a > logger object with the name of the module
the decorated function is in > (``decorated_function.__module__``) > >
Default: Creates a new logger with the name
``decorated_function.__module__``

**on\_exceptions** *(optional)* > A tuple containing exception classes
or a single exception, which should get > caught and trigger the logging
of the ``log_on_error`` decorator. > > Default: tuple() (No exceptions
will get caught)

**reraise** *(optional)* > Controls if caught exceptions should get
reraised after logging > > Default: False

**exception\_format\_variable** *(optional)* > The variable name one can
use in the message to reference the caught exception > raised in the
decorated function > e.g. @log\_on\_error(ERROR, "Error was: {e!r}",
...) > > Default: "e"

log\_exception
^^^^^^^^^^^^^^

**log\_level** > The log level at which the message should be send

**message** > The message to log

**logger** *(optional)* > An alternative logger object. If no logger is
given logdecorator creates a > logger object with the name of the module
the decorated function is in > (``decorated_function.__module__``) > >
Default: Creates a new logger with the name
``decorated_function.__module__``

**on\_exceptions** *(optional)* > A tuple containing exception classes
or a single exception, which should get > caught and trigger the logging
of the ``log_on_error`` decorator. > > Default: tuple() (No exceptions
will get caught)

**reraise** *(optional)* > Controls if caught exceptions should get
reraised after logging > > Default: False

**exception\_format\_variable** *(optional)* > The variable name one can
use in the message to reference the caught exception > raised in the
decorated function > e.g. @log\_on\_error(ERROR, "Error was: {e!r}",
...) > > Default: "e"

.. |Downloads| image:: https://pepy.tech/badge/logdecorator
   :target: https://pepy.tech/project/logdecorator
