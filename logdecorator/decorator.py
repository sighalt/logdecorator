import inspect
import logging
from functools import wraps
from warnings import warn


class LoggingDecorator(object):

    def __init__(self, log_level, message, *, logger=None):
        self.log_level = log_level
        self.message = message
        self._logger = logger

    def before_execution(self, fn, *args, **kwargs):
        pass

    def after_execution(self, fn, result, *args, **kwargs):
        pass

    def on_error(self, fn, exception, *args, **kwargs):
        raise exception

    @staticmethod
    def log(logger, log_level, msg):
        logger.log(log_level, msg)

    def get_logger(self, fn):
        if self._logger is None:
            self._logger = logging.getLogger(fn.__module__)

        return self._logger

    @staticmethod
    def build_extensive_kwargs(fn, *args, **kwargs):
        function_signature = inspect.signature(fn)
        extensive_kwargs = function_signature.bind_partial(*args, **kwargs)

        return extensive_kwargs.arguments

    def __call__(self, fn):

        @wraps(fn)
        def wrapper(*args, **kwargs):
            self.before_execution(fn, *args, **kwargs)

            try:
                result = fn(*args, **kwargs)
            except Exception as e:
                self.on_error(fn, e, *args, **kwargs)
            else:
                self.after_execution(fn, result, *args, **kwargs)

                return result

        return wrapper


class log_on_start(LoggingDecorator):

    def before_execution(self, fn, *args, **kwargs):
        logger = self.get_logger(fn)
        extensive_kwargs = self.build_extensive_kwargs(fn, *args, **kwargs)
        msg = self.message.format(**extensive_kwargs)

        self.log(logger, self.log_level, msg)


class log_on_end(LoggingDecorator):

    def __init__(self, log_level, message, *, logger=None,
                 result_format_variable="result"):
        super().__init__(log_level, message, logger=logger)
        self.result_format_variable = result_format_variable

    def after_execution(self, fn, result, *args, **kwargs):
        logger = self.get_logger(fn)
        extensive_kwargs = self.build_extensive_kwargs(fn, *args, **kwargs)
        extensive_kwargs[self.result_format_variable] = result
        msg = self.message.format(**extensive_kwargs)

        self.log(logger, self.log_level, msg)


class log_on_error(LoggingDecorator):

    def __init__(self, log_level, message, *, logger=None,
                 on_exceptions=None, reraise=None,
                 exception_format_variable="e"):
        super().__init__(log_level, message, logger=logger)
        self.on_exceptions = on_exceptions

        if reraise is None:
            warn("The default value of the `reraise` parameter will be changed "
                 "to `True` in the future. If you rely on catching the"
                 "exception, you should explicitly set `reraise` to `False`.",
                 category=DeprecationWarning)
            reraise = False

        self.reraise = reraise
        self.exception_format_variable = exception_format_variable

    def _log_error(self, fn, exception, *args, **kwargs):
        logger = self.get_logger(fn)
        extensive_kwargs = self.build_extensive_kwargs(fn, *args, **kwargs)
        extensive_kwargs[self.exception_format_variable] = exception
        msg = self.message.format(**extensive_kwargs)

        self.log(logger, self.log_level, msg)

    def on_error(self, fn, exception, *args, **kwargs):
        try:
            raise exception
        except self.on_exceptions:
            self._log_error(fn, exception, *args, **kwargs)

            if self.reraise:
                raise


class log_exception(log_on_error):

    def __init__(self, log_level, message, *, logger=None, on_exceptions=None,
                 reraise=None, exception_format_variable="e"):
        if log_level != logging.ERROR:
            warn("`log_exception` can only log into ERROR log level")

        super().__init__(log_level, message, logger=logger,
                         on_exceptions=on_exceptions, reraise=reraise,
                         exception_format_variable=exception_format_variable)

    @staticmethod
    def log(logger, log_level, msg):
        logger.exception(msg)
