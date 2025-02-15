import inspect
import logging
from functools import wraps
from logging import Logger, Handler
from typing import Callable, Any, Dict, Tuple, Optional, Union, Type, TypeVar, ParamSpec, Optional
from warnings import warn

P = ParamSpec("P")
T = TypeVar("T")


class DecoratorMixin(object):

    def execute(self, fn: Callable[P, T], *args: P.args, **kwargs: P.kwargs) -> Optional[T]:
        return fn(*args, **kwargs)

    def __call__(self, fn: Callable[P, T]) -> Callable[P, Optional[T]]:

        @wraps(fn)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> Optional[T]:
            return self.execute(fn, *args, **kwargs)

        return wrapper


class LoggingDecorator(DecoratorMixin):

    def __init__(self,
                 log_level: int,
                 message: str,
                 *,
                 logger: Optional[Logger] = None,
                 handler: Optional[Handler] = None,
                 callable_format_variable: str = "callable"):
        self.log_level = log_level
        self.message = message

        if handler is not None and logger is not None:
            warn("Detected mixed use of `handler` and `logger` argument. The handler argument is ignored.")
            handler = None

        self._logger = logger
        self._handler = handler
        self.callable_format_variable = callable_format_variable

    @staticmethod
    def log(logger: Logger, log_level: int, msg: str) -> None:
        logger.log(log_level, msg)

    def get_logger(self, fn: Callable[P, T]) -> Logger:
        if self._logger is None:
            self._logger = logging.getLogger(fn.__module__)

            if self._handler is not None:
                self._logger.addHandler(self._handler)

        return self._logger

    @staticmethod
    def build_extensive_kwargs(fn: Callable[P, T], *args: P.args, **kwargs: P.kwargs) -> Dict[str, Any]:
        function_signature = inspect.signature(fn)
        bound_arguments = function_signature.bind_partial(*args, **kwargs)

        extensive_kwargs = {
            param_name: bound_arguments.arguments.get(param_name, param_object.default)
            for param_name, param_object
            in bound_arguments.signature.parameters.items()
        }

        return extensive_kwargs

    def build_msg(self, fn: Callable[P, T], fn_args: Any, fn_kwargs: Any,
                  **extra: Any) -> str:
        format_kwargs = self.build_extensive_kwargs(fn, *fn_args, **fn_kwargs)
        extra[self.callable_format_variable] = fn
        format_kwargs.update(extra)

        return self.message.format(**format_kwargs)


class log_on_start(LoggingDecorator):

    def _do_logging(self, fn: Callable[P, T], *args: P.args, **kwargs: P.kwargs) -> None:
        logger = self.get_logger(fn)
        msg = self.build_msg(fn, fn_args=args, fn_kwargs=kwargs)

        self.log(logger, self.log_level, msg)

    def execute(self, fn: Callable[P, T], *args: P.args, **kwargs: P.kwargs) -> Optional[T]:
        self._do_logging(fn, *args, **kwargs)
        return super().execute(fn, *args, **kwargs)


class log_on_end(LoggingDecorator):

    def __init__(self, log_level: int, message: str, *, logger: Optional[Logger] = None,
                 handler: Optional[Handler] = None, callable_format_variable: str = "callable",
                 result_format_variable: str = "result"):
        super().__init__(log_level, message, logger=logger, handler=handler,
                         callable_format_variable=callable_format_variable)
        self.result_format_variable = result_format_variable

    def _do_logging(self, fn: Callable[P, T], result: T, *args: P.args, **kwargs: P.kwargs) -> None:
        logger = self.get_logger(fn)
        extra = {
            self.result_format_variable: result
        }
        msg = self.build_msg(fn, fn_args=args, fn_kwargs=kwargs, **extra)

        self.log(logger, self.log_level, msg)

    def execute(self, fn: Callable[P, T], *args: P.args, **kwargs: P.kwargs) -> Optional[T]:
        result = super().execute(fn, *args, **kwargs)
        self._do_logging(fn, result, *args, **kwargs)

        return result


class log_on_error(LoggingDecorator):

    def __init__(self,
                 log_level: int,
                 message: str,
                 *,
                 logger: Optional[Logger] = None,
                 handler: Optional[Handler] = None,
                 callable_format_variable: str = "callable",
                 on_exceptions: Optional[Union[Type[BaseException], Tuple[Type[BaseException]], Tuple[()]]] = None,
                 reraise: bool = True,
                 exception_format_variable: str = "e"):
        super().__init__(log_level, message, logger=logger, handler=handler,
                         callable_format_variable=callable_format_variable)
        self.on_exceptions: Union[Type[BaseException], Tuple[Type[BaseException]], Tuple[()]] = on_exceptions or ()
        self.reraise = reraise
        self.exception_format_variable = exception_format_variable

    def _do_logging(self, fn: Callable[P, T], exception: BaseException, *args: P.args, **kwargs: P.kwargs
                    ) -> None:
        logger = self.get_logger(fn)
        extra: Dict[str, Any] = {
            self.exception_format_variable: exception
        }
        msg = self.build_msg(fn, fn_args=args, fn_kwargs=kwargs, **extra)

        self.log(logger, self.log_level, msg)

    def execute(self, fn: Callable[P, T], *args: P.args, **kwargs: P.kwargs) -> Optional[T]:
        try:
            return super().execute(fn, *args, **kwargs)
        except BaseException as e:
            self.on_error(fn, e, *args, **kwargs)
            return None

    def on_error(self, fn: Callable[P, T], exception: BaseException, *args: P.args, **kwargs: P.kwargs) -> None:
        try:
            raise exception
        except self.on_exceptions:
            self._do_logging(fn, exception, *args, **kwargs)

            if self.reraise:
                raise

class log_exception(log_on_error):

    def __init__(self, message: str, *, logger: Optional[Logger] = None,
                 handler: Optional[Handler] = None, callable_format_variable: str = "callable",
                 on_exceptions:  Optional[Union[Type[BaseException], Tuple[Type[BaseException]], Tuple[()]]] = None,
                 reraise: bool = True, exception_format_variable: str = "e"):
        super().__init__(logging.ERROR, message, logger=logger,
                         handler=handler, callable_format_variable=callable_format_variable,
                         on_exceptions=on_exceptions, reraise=reraise,
                         exception_format_variable=exception_format_variable)

    @staticmethod
    def log(logger: Logger, log_level: Union[str, int], msg: str) -> None:
        logger.exception(msg)
