import logging
from unittest import TestCase
from unittest.mock import Mock, patch

from .decorator import log_exception, log_on_start, log_on_error, log_on_end


def test_func(arg1, arg2, kwarg1=None, kwarg2=None):
    return arg1 + arg2


class TestException(Exception):
    pass


class MockLoggingHandler(logging.Handler):
    """Mock logging handler to check for expected logs.

    Messages are available from an instance's ``messages`` dict, in order, indexed by
    a lowercase log level string (e.g., 'debug', 'info', etc.).
    """

    def __init__(self, *args, **kwargs):
        self.messages = {'debug': [], 'info': [], 'warning': [], 'error': [],
                         'critical': []}
        super(MockLoggingHandler, self).__init__(*args, **kwargs)

    def emit(self, record):
        "Store a message from ``record`` in the instance's ``messages`` dict."
        try:
            self.messages[record.levelname.lower()].append(record.getMessage())
        except Exception:
            self.handleError(record)

    def reset(self):
        self.acquire()
        try:
            for message_list in self.messages.values():
                message_list.clear()
        finally:
            self.release()


class TestDecorators(TestCase):

    def setUp(self):
        self.logger = logging.Logger("mocked")
        self.log_handler = MockLoggingHandler()
        self.log_handler.setFormatter("%(msg)s")
        self.logger.addHandler(self.log_handler)

    def test_log_on_start(self):
        dec = log_on_start(logging.INFO,
                           "test message {arg1:d}, {arg2:d}",
                           logger=self.logger)
        fn = dec(test_func)
        fn(1, 2)
        self.assertIn("test message 1, 2", self.log_handler.messages["info"])

    def test_log_on_end(self):
        dec = log_on_end(logging.INFO,
                         "test message {arg1:d}, {arg2:d} => {result:d}",
                         logger=self.logger)
        fn = dec(test_func)
        fn(1, 2)
        self.assertIn("test message 1, 2 => 3",
                      self.log_handler.messages["info"])

    def test_log_on_error(self):
        mocked_func = Mock(side_effect=TestException("test exception"))

        dec = log_on_error(logging.INFO,
                           "test message {e!r}",
                           logger=self.logger,
                           on_exceptions=TestException)
        fn = dec(mocked_func)
        fn(1, 2)
        self.assertIn("test message TestException('test exception',)",
                      self.log_handler.messages["info"])

    def test_log_on_error_reraise(self):
        mocked_func = Mock(side_effect=TestException("test exception"))

        dec = log_on_error(logging.INFO,
                           "test message {e!r}",
                           logger=self.logger,
                           on_exceptions=TestException,
                           reraise=True)
        fn = dec(mocked_func)

        with self.assertRaises(TestException):
            fn(1, 2)

        self.assertIn("test message TestException('test exception',)",
                      self.log_handler.messages["info"])

    def test_log_exception(self):
        self.logger.exception = Mock()
        dec = log_exception(logging.ERROR,
                            "test message",
                            logger=self.logger,
                            on_exceptions=TypeError)
        fn = dec(test_func)
        fn(2, "asd")
        self.assertEqual(self.logger.exception.call_count, 1)
