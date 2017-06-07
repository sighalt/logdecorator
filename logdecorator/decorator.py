import inspect
import logging
from functools import wraps


class LoggingDecorator(object):
    """
    Base decorator factory.

    The instances of this classes can be used as logging decorators.
    """

    def __init__(self,
                 log_before_execution=False,
                 log_after_execution=False,
                 log_on_exception=False):
        """
        Initializer

        :param log_before_execution: enable logging before execution of the
        decorated function
        :param log_after_execution: enable logging after execution of the
        decorated function
        :param log_on_exception: enable logging on error in the decorated
        function
        :param reraise_exceptions: En-/disable reraising of catched exceptions
        """
        self.log_before_execution = log_before_execution
        self.log_after_execution = log_after_execution
        self.log_on_exception = log_on_exception

    @staticmethod
    def build_extensive_kwargs(fn, *args, **kwargs):
        function_signature = inspect.signature(fn)
        extensive_kwargs = function_signature.bind_partial(*args, **kwargs)

        return extensive_kwargs.arguments

    @staticmethod
    def get_logger(function):
        return logging.getLogger(function.__module__)

    def __call__(self, log_level, message, on_exceptions=None,
                 reraise=False, logger=None, result_format_variable="result",
                 exception_format_variable="e"):
        exceptions = tuple(on_exceptions or [])

        def decorator(function):
            nonlocal logger
            logger = logger or self.get_logger(function)

            @wraps(function)
            def wrapper(*args, **kwargs):
                nonlocal message
                nonlocal result_format_variable
                nonlocal exception_format_variable
                extensive_kwargs = self.build_extensive_kwargs(function,
                                                               *args,
                                                               **kwargs)

                if self.log_before_execution:
                    self.before_execution(logger,
                                          log_level,
                                          message.format(**extensive_kwargs))

                try:
                    result = function(*args, **kwargs)
                except exceptions as e:
                    if log_on_error:
                        extensive_kwargs[exception_format_variable] = e
                        self.on_error(logger,
                                      log_level,
                                      message.format(**extensive_kwargs))

                    if reraise:
                        raise

                    return

                if self.log_after_execution:
                    extensive_kwargs[result_format_variable] = result
                    self.after_execution(logger,
                                         log_level,
                                         message.format(**extensive_kwargs))

                return result

            return wrapper

        return decorator

    @staticmethod
    def log(logger, log_level, message):
        logger.log(log_level, message)

    before_execution = log
    after_execution = log
    on_error = log


log_on_start = LoggingDecorator(log_before_execution=True)
log_on_end = LoggingDecorator(log_after_execution=True)
log_on_error = LoggingDecorator(log_on_exception=True)
