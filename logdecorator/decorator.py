import inspect
import logging
from functools import wraps
from warnings import warn


class DecoratorMixin(object):

    def execute(self, fn, *args, **kwargs):
        return fn(*args, **kwargs)

    def __call__(self, fn):

        @wraps(fn)
        def wrapper(*args, **kwargs):
            return self.execute(fn, *args, **kwargs)

        return wrapper


class LoggingDecorator(DecoratorMixin):

    def __init__(self, log_level, message, *, logger=None, handler=None, callable_format_variable="callable"):
        self.log_level = log_level
        self.message = message

        if handler is not None and logger is not None:
            warn("Detected mixed use of `handler` and `logger` argument. The handler argument is ignored.")
            handler = None

        self._logger = logger
        self._handler = handler
        self.callable_format_variable = callable_format_variable

    @staticmethod
    def log(logger, log_level, msg):
        logger.log(log_level, msg)

    def get_logger(self, fn):
        if self._logger is None:
            self._logger = logging.getLogger(fn.__module__)

            if self._handler is not None:
                self._logger.addHandler(self._handler)

        return self._logger

    @staticmethod
    def build_extensive_kwargs(fn, *args, **kwargs):
        function_signature = inspect.signature(fn)
        bound_arguments = function_signature.bind_partial(*args, **kwargs)

        extensive_kwargs = {
            param_name: bound_arguments.arguments.get(param_name, param_object.default)
            for param_name, param_object
            in bound_arguments.signature.parameters.items()
        }

        return extensive_kwargs

    def build_msg(self, fn: FunctionType, fn_args: Any, fn_kwargs: Any,
                  **extra: Any) -> str:
        format_kwargs = self.build_extensive_kwargs(fn, *fn_args, **fn_kwargs)
        extra[self.callable_format_variable] = fn
        format_kwargs.update(extra)

        return self.message.format(**format_kwargs)


class log_on_start(LoggingDecorator):

    def _do_logging(self, fn, *args, **kwargs):
        logger = self.get_logger(fn)
        msg = self.build_msg(fn, fn_args=args, fn_kwargs=kwargs)

        self.log(logger, self.log_level, msg)

    def execute(self, fn, *args, **kwargs):
        self._do_logging(fn, *args, **kwargs)
        return super().execute(fn, *args, **kwargs)


class log_on_end(LoggingDecorator):

    def __init__(self, log_level, message, *, logger=None,
                 handler=None, callable_format_variable="callable",
                 result_format_variable="result"):
        super().__init__(log_level, message, logger=logger, handler=handler,
                         callable_format_variable=callable_format_variable)
        self.result_format_variable = result_format_variable

    def _do_logging(self, fn, result, *args, **kwargs):
        logger = self.get_logger(fn)
        extra = {
            self.result_format_variable: result
        }
        msg = self.build_msg(fn, fn_args=args, fn_kwargs=kwargs, **extra)

        self.log(logger, self.log_level, msg)

    def execute(self, fn, *args, **kwargs):
        result = super().execute(fn, *args, **kwargs)
        self._do_logging(fn, result, *args, **kwargs)

        return result


class log_on_error(LoggingDecorator):

    def __init__(self, log_level, message, *, logger=None,
                 handler=None, callable_format_variable="callable",
                 on_exceptions=None, reraise=True,
                 exception_format_variable="e"):
        super().__init__(log_level, message, logger=logger, handler=handler,
                         callable_format_variable=callable_format_variable)
        self.on_exceptions = on_exceptions
        self.reraise = reraise
        self.exception_format_variable = exception_format_variable

    def _do_logging(self, fn, exception, *args, **kwargs):
        logger = self.get_logger(fn)
        extra = {
            self.exception_format_variable: exception
        }
        msg = self.build_msg(fn, fn_args=args, fn_kwargs=kwargs, **extra)

        self.log(logger, self.log_level, msg)

    def execute(self, fn, *args, **kwargs):
        try:
            return super().execute(fn, *args, **kwargs)
        except Exception as e:
            self.on_error(fn, e, *args, **kwargs)

    def on_error(self, fn, exception, *args, **kwargs):
        try:
            raise exception
        except self.on_exceptions:
            self._do_logging(fn, exception, *args, **kwargs)

            if self.reraise:
                raise


class log_exception(log_on_error):

    def __init__(self, message, *, logger=None,
                 handler=None, callable_format_variable="callable",
                 on_exceptions=None,
                 reraise=True, exception_format_variable="e"):
        super().__init__(logging.ERROR, message, logger=logger,
                         handler=handler, callable_format_variable=callable_format_variable,
                         on_exceptions=on_exceptions, reraise=reraise,
                         exception_format_variable=exception_format_variable)

    @staticmethod
    def log(logger, log_level, msg):
        logger.exception(msg)
