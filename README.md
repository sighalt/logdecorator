# Logdecorator

Move logging code out of your business logic with python decorators.

Logging is a nice tool in your toolbox for tracing bugs and getting a better
sense how your application is working in production. But if you are like me, you
often omit logging code, so it will not hide business logic or feature your code
with complexity.

Fortunately pythons decorator now came to our rescue and provides us with a nice
library to add logging to our code without stealing readability and
understandability.

## Installation

Installation is as easy as it can get:

```bash
$ pip install logdecorator
```

## How to use it

Imagine a function `download` with no arguments and some download code in it.

```python
def download():
    # some download code


if __name__ == "__main__":
    download()
```

Say you are going to launch your new tool but want to add some logging before
releasing the kraken. Your code will probably look something like the following:

```python
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

```

You just added at least a couple lines of code which are eventually stumbling in
your way when you are trying to understand your business logic to find a bug.
But what's even worse is, that you added an additional indentation (try:...
except: ...) just for the sake of logging.

With logdecorator you can leave your code nearly as it was and reach the same
goals.

```python
import logging
from logdecorator import log_on_start, log_on_end, log_on_error
from .exceptions import MyException1, MyException2


@log_on_start(logging.DEBUG, "Start downloading")
@log_on_error(logging.ERROR, "Error on downloading",
              on_exceptions=[MyException1, MyException2],
              reraise=True)
@log_on_end(logging.DEBUG, "Downloading finished successfully")
def download():
    # some download code


if __name__ == "__main__":
    download()

```

Maybe the improvement to the previous snippet does not seem great for you but if
you actually fill in business logic into `# some download code` it should become
obvious :)


## What logdecorator can do for you

### Decorators

logdecorator provides three different built-in decorators:

 * log_on_start
 * log_on_end
 * log_on_error

whose behaviour corresponds to their names.


### Arguments

Each decorator takes the following arguments:

**log_level**
> The log level at which the message should be send

**message**
> The message to log

**on_exceptions** *(optional)*
> A list containing exception classes which should get caught and trigger the
> logging of the `log_on_error` decorator.
>
> Default: tuple() (No exceptions will get caught)

**logger** *(optional)*
> An alternative logger object. If no logger is given logdecorator creates a
> logger object with the name of the module the decorated function is in
> (`decorated_function.__module__`)
>
> Default: Creates a new logger with the name `decorated_function.__module__`

**reraise** *(optional)*
> Controls if caught exceptions should get reraised after logging
>
> Default: False

**result_format_variable** *(optional)*
> The variable name one can use in the message to reference the result of the
> decorated function
> e.g. @log_on_end(DEBUG, "Result was: {result!r}")
>
> Default: "result"

**exception_format_variable** *(optional)*
> The variable name one can use in the message to reference the caught exception
> raised in the decorated function
> e.g. @log_on_error(ERROR, "Error was: {e!r}", ...)
>
> Default: "e"

### Use variables in messages

The message, given to the decorator, is treated as a python format string which
takes the functions arguments as format arguments.

Sticking to the previous example one could write:

```python

import logging
from logdecorator import log_on_start
from .exceptions import MyException1, MyException2


@log_on_start(logging.DEBUG, "Start downloading '{url:s}'")
def download(url):
    # some download code


if __name__ == "__main__":
    download("http://my.file.com/file.bin")

```

Which results in the message `Start downloading 'http://my.file.com/file.bin'`
gets logged.
