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
`blog <https://www.sighalt.de/a-new-logdecorator-version-is-available-o.html>`__
or in the `changelog <CHANGES.rst>`_.

Installation
------------

Installation is as easy as it can get:

.. code:: bash

    $ pip install logdecorator

How to use it
-------------

tl;dr
~~~~~

.. code:: python

    import logging
    import requests
    from logdecorator import log_on_start, log_on_end, log_on_error, log_exception


    @log_on_start(logging.DEBUG, "Start downloading {url:s}...")
    @log_on_error(logging.ERROR, "Error on downloading {url:s}: {e!r}",
                  on_exceptions=IOError,
                  reraise=True)
    @log_on_end(logging.DEBUG, "Downloading {url:s} finished successfully within {result.elapsed!s}")
    def download(url):
        # some code
        response = requests.get(url)
        # some more code
        return response


    logging.basicConfig(level=logging.DEBUG)

    download("https://www.sighalt.de")
    # DEBUG:__main__:Start downloading https://www.sighalt.de...
    # DEBUG:urllib3.connectionpool:Starting new HTTPS connection (1): www.sighalt.de
    # DEBUG:urllib3.connectionpool:https://www.sighalt.de:443 "GET / HTTP/1.1" 200 None
    # DEBUG:__main__:Downloading https://www.sighalt.de finished successfully within 0:00:00.130960

    download("https://www.sighalt.der")
    # DEBUG:__main__:Start downloading https://www.sighalt.der...
    # DEBUG:urllib3.connectionpool:Starting new HTTPS connection (1): www.sighalt.der
    # ERROR:__main__:Error on downloading https://www.sighalt.der: ConnectionError(MaxRetryError("
    # HTTPSConnectionPool(host='www.sighalt.der', port=443): Max retries exceeded with url: /
    # (Caused by NewConnectionError('<urllib3.connection.VerifiedHTTPSConnection object at 0x7fe3fc4b5320>:
    # Failed to establish a new connection: [Errno -2] Name or service not known',))",),)

Long story
~~~~~~~~~~

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

Additionally logdecorator supports decorating async callables with the decorators:

-  async\_log\_on\_start
-  async\_log\_on\_end
-  async\_log\_on\_error
-  async\_log\_exception

These decorators are found at logdecorator.asyncio


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


Documentation
~~~~~~~~~~~~~

format variables
^^^^^^^^^^^^^^^^

The following variable names can be used to construct the message:

.. list-table::
    :header-rows: 1

    * - Default variable name
      - Description
      - log_on_start
      - log_on_end
      - log_on_error
      - log_exception
    * - callable
      - The decorated callable
      - Yes
      - Yes
      - Yes
      - Yes
    * - *args/kwargs*
      - Whatever arguments given to the callable can be used in the logging message
      - Yes
      - Yes
      - Yes
      - Yes
    * - result
      - Whatever the decorated callable returns
      - No
      - Yes
      - No
      - No
      - No
    * - e
      - The exception raised while executing the callable
      - No
      - No
      - Yes
      - Yes


log\_on\_start / async\_log\_on\_start
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. list-table::
    :header-rows: 1

    * - Argument
      - required?
      - Description
    * - log\_level
      - yes
      - The log level at which the message should be send
    * - message
      - yes
      - The message to log
    * - logger
      - no
      - An alternative logger object. If no logger is given logdecorator creates a logger object with the name of the module the decorated function is in (``decorated_function.__module__``) Default: Creates a new logger with the name ``decorated_function.__module__``
    * - callable_format_variable
      - no
      - The variable name one can use in the message to reference the decorated callable. e.g. @log\_on\_start(ERROR, "Called {callable.__name__:s}", ...) Default: "callable"


log\_on\_end / async\_log\_on\_end
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. list-table::
    :header-rows: 1

    * - Argument
      - required?
      - Description
    * - log\_level
      - yes
      - The log level at which the message should be send
    * - message
      - yes
      - The message to log
    * - logger
      - no
      - An alternative logger object. If no logger is given logdecorator creates a logger object with the name of the module the decorated function is in (``decorated_function.__module__``) Default: Creates a new logger with the name ``decorated_function.__module__``
    * - result\_format\_variable
      - no
      - The variable name one can use in the message to reference the result of the > decorated function e.g. @log\_on\_end(DEBUG, "Result was: {result!r}") Default: "result"
    * - callable_format_variable
      - no
      - The variable name one can use in the message to reference the decorated callable. e.g. @log\_on\_start(ERROR, "Called {callable.__name__:s}", ...) Default: "callable"



log\_on\_error / async\_log\_on\_error
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. list-table::
    :header-rows: 1

    * - Argument
      - required?
      - Description
    * - log\_level
      - yes
      - The log level at which the message should be send
    * - message
      - yes
      - The message to log
    * - logger
      - no
      - An alternative logger object. If no logger is given logdecorator creates a logger object with the name of the module the decorated function is in (``decorated_function.__module__``) Default: Creates a new logger with the name ``decorated_function.__module__``
    * - on\_exceptions
      - no
      - A tuple containing exception classes or a single exception, which should get caught and trigger the logging of the ``log_on_error`` decorator. Default: tuple() (No exceptions will get caught)
    * - reraise
      - no
      - Controls if caught exceptions should get reraised after logging. Default: True
    * - exception\_format\_variable
      - no
      - The variable name one can use in the message to reference the caught exception raised in the decorated function > e.g. @log\_on\_error(ERROR, "Error was: {e!r}", ...) Default: "e"
    * - callable_format_variable
      - no
      - The variable name one can use in the message to reference the decorated callable. e.g. @log\_on\_start(ERROR, "Called {callable.__name__:s}", ...) Default: "callable"


log\_exception / async\_log\_exception
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. list-table::
    :header-rows: 1

    * - Argument
      - required?
      - Description
    * - log\_level
      - yes
      - The log level at which the message should be send
    * - message
      - yes
      - The message to log
    * - logger
      - no
      - An alternative logger object. If no logger is given logdecorator creates a logger object with the name of the module the decorated function is in (``decorated_function.__module__``) Default: Creates a new logger with the name ``decorated_function.__module__``
    * - on\_exceptions
      - no
      - A tuple containing exception classes or a single exception, which should get caught and trigger the logging of the ``log_on_error`` decorator. Default: tuple() (No exceptions will get caught)
    * - reraise
      - no
      -  Controls if caught exceptions should get reraised after logging. Default: False
    * - exception\_format\_variable
      - no
      - The variable name one can use in the message to reference the caught exception raised in the decorated function e.g. @log\_on\_error(ERROR, "Error was: {e!r}", ...) Default: "e"
    * - callable_format_variable
      - no
      - The variable name one can use in the message to reference the decorated callable. e.g. @log\_on\_start(ERROR, "Called {callable.__name__:s}", ...) Default: "callable"

.. |Downloads| image:: https://pepy.tech/badge/logdecorator
   :target: https://pepy.tech/project/logdecorator
