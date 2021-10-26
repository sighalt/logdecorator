from functools import wraps
from types import FunctionType
from typing import Callable, Any

from logdecorator import log_on_start, log_on_end, log_on_error, log_exception
from logdecorator.decorator import DecoratorMixin


class AsyncDecoratorMixin(DecoratorMixin):

    async def execute(self, fn: FunctionType, *args: Any, **kwargs: Any) -> Any:
        return await fn(*args, **kwargs)

    def __call__(self, fn: FunctionType) -> Callable[..., Any]:

        @wraps(fn)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            return await self.execute(fn, *args, **kwargs)

        return wrapper


class async_log_on_start(AsyncDecoratorMixin, log_on_start):

    async def execute(self, fn: FunctionType, *args: Any, **kwargs: Any) -> Any:
        self._do_logging(fn, *args, **kwargs)
        return await super().execute(fn, *args, **kwargs)


class async_log_on_end(AsyncDecoratorMixin, log_on_end):

    async def execute(self, fn: FunctionType, *args: Any, **kwargs: Any) -> Any:
        result = await super().execute(fn, *args, **kwargs)
        self._do_logging(fn, result, *args, **kwargs)

        return result


class async_log_on_error(AsyncDecoratorMixin, log_on_error):

    async def execute(self, fn: FunctionType, *args: Any, **kwargs: Any) -> Any:
        try:
            return await super().execute(fn, *args, **kwargs)
        except Exception as e:
            self.on_error(fn, e, *args, **kwargs)


class async_log_exception(async_log_on_error, log_exception):

    async def execute(self, fn: FunctionType, *args: Any, **kwargs: Any) -> Any:
        return await super().execute(fn, *args, **kwargs)
