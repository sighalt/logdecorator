from functools import wraps
from typing import Callable, Any, TypeVar, ParamSpec, Awaitable, cast, Optional

from logdecorator import log_on_start, log_on_end, log_on_error, log_exception
from logdecorator.decorator import DecoratorMixin

P = ParamSpec("P")
T = TypeVar("T")


class AsyncDecoratorMixin(DecoratorMixin):

    async def execute(self, fn: Callable[P, Awaitable[T]], *args: P.args, **kwargs: P.kwargs) -> Optional[T]: # type: ignore[override]
        return await fn(*args, **kwargs)

    def __call__(self, fn: Callable[P, Awaitable[T]]) -> Callable[P, Awaitable[Optional[T]]]: # type: ignore[override]

        @wraps(fn)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> Optional[T]:
            return await self.execute(fn, *args, **kwargs)

        return cast(Callable[P, Awaitable[Optional[T]]], wrapper)


class async_log_on_start(AsyncDecoratorMixin, log_on_start):

    async def execute(self, fn: Callable[P, Awaitable[Optional[T]]], *args: P.args, **kwargs: P.kwargs) -> Optional[T]: # type: ignore[override]
        self._do_logging(fn, *args, **kwargs)
        return await super().execute(fn, *args, **kwargs)


class async_log_on_end(AsyncDecoratorMixin, log_on_end):

    async def execute(self, fn: Callable[P, Awaitable[Optional[T]]], *args: P.args, **kwargs: P.kwargs) -> Optional[T]: # type: ignore[override]
        result = await super().execute(fn, *args, **kwargs)
        self._do_logging(fn, result, *args, **kwargs)
        return result


class async_log_on_error(AsyncDecoratorMixin, log_on_error):

    async def execute(self, fn: Callable[P, Awaitable[Optional[T]]], *args: P.args, **kwargs: P.kwargs) -> Optional[T]: # type: ignore[override]
        try:
            return await super().execute(fn, *args, **kwargs)
        except Exception as e:
            self.on_error(fn, e, *args, **kwargs)
            return None


class async_log_exception(async_log_on_error, log_exception):

    async def execute(self, fn: Callable[P, Awaitable[Optional[T]]], *args: P.args, **kwargs: P.kwargs) -> Optional[T]: # type: ignore[override]
        return await super().execute(fn, *args, **kwargs)
