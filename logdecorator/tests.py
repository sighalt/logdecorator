from unittest import TestCase
from unittest.mock import Mock, patch

from .decorator import LoggingDecorator


def test_func(arg1, arg2, kwarg1=None, kwarg2=None):
    return


class TestLoggingDecorator(TestCase):

    def test_build_extensive_kwargs_only_args(self):
        dec = LoggingDecorator()
        extensive_kwargs = dec.build_extensive_kwargs(test_func, "arg1", "arg2")

        self.assertEqual({"arg1": "arg1", "arg2": "arg2"},
                         extensive_kwargs)

    def test_build_extensive_kwargs_only_kwargs(self):
        dec = LoggingDecorator()
        extensive_kwargs = dec.build_extensive_kwargs(test_func,
                                                      arg1="arg1",
                                                      arg2="arg2",
                                                      kwarg1="kwarg1")

        self.assertEqual({"arg1": "arg1", "arg2": "arg2", "kwarg1": "kwarg1"},
                         extensive_kwargs)

    def test_build_extensive_kwargs_mixed(self):
        dec = LoggingDecorator()
        extensive_kwargs = dec.build_extensive_kwargs(test_func,
                                                      "arg1",
                                                      arg2="arg2",
                                                      kwarg1="kwarg1")

        self.assertEqual({"arg1": "arg1", "arg2": "arg2", "kwarg1": "kwarg1"},
                         extensive_kwargs)

    def test_catch_exception(self):
        dec = LoggingDecorator()
        MyExc = type("MyExc", (Exception,), {})
        function = Mock(side_effect=MyExc)
        decorated_function = (dec(0, "testmessage", on_exceptions=[MyExc],
                                  reraise=False)
                              (function))

        decorated_function()
        function.assert_called_once()

    def test_reraise_exception(self):
        dec = LoggingDecorator()
        MyExc = type("MyExc", (Exception,), {})
        function = Mock(side_effect=MyExc)
        decorated_function = (dec(0, "testmessage", on_exceptions=[MyExc],
                                  reraise=True)
                              (function))

        with self.assertRaises(MyExc):
            decorated_function()

    def test_before_execution_hook(self):
        dec = LoggingDecorator(log_before_execution=True)
        dec.before_execution = Mock()
        dec.after_execution = Mock()
        dec.on_error = Mock()
        function = Mock()
        decorated_function = (dec(0, "testmessage")(function))

        decorated_function()

        function.assert_called_once()
        dec.before_execution.assert_called_once()
        dec.after_execution.assert_not_called()
        dec.on_error.assert_not_called()

    def test_after_execution_hook(self):
        dec = LoggingDecorator(log_after_execution=True)
        dec.before_execution = Mock()
        dec.after_execution = Mock()
        dec.on_error = Mock()
        function = Mock()
        decorated_function = (dec(0, "testmessage")(function))

        decorated_function()

        function.assert_called_once()
        dec.before_execution.assert_not_called()
        dec.after_execution.assert_called_once()
        dec.on_error.assert_not_called()

    def test_on_error(self):
        dec = LoggingDecorator(log_after_execution=True)
        dec.before_execution = Mock()
        dec.after_execution = Mock()
        dec.on_error = Mock()
        function = Mock(side_effect=Exception)
        decorated_function = (dec(0, "testmessage", on_exceptions=[Exception],
                                  reraise=False)
                              (function))

        decorated_function()

        function.assert_called_once()
        dec.before_execution.assert_not_called()
        dec.after_execution.assert_not_called()
        dec.on_error.assert_called_once()

    def test_autocreate_logger(self):
        dec = LoggingDecorator()
        function = Mock()

        with patch("logging.getLogger", Mock()) as getLogger:
            decorated_function = dec(0, "test")(function)
            decorated_function()
            getLogger.assert_called_once()

    def test_custom_logger(self):
        dec = LoggingDecorator()
        function = Mock()
        custom_logger = Mock()

        with patch("logging.getLogger", Mock()) as getLogger:
            decorated_function = dec(0, "test", logger=custom_logger)(function)
            decorated_function()
            getLogger.assert_not_called()

    def test_message_formatting(self):
        dec = LoggingDecorator(log_before_execution=True)
        logger = Mock()
        message = "Hello world. My name is {arg1:s}, I am {arg2:d} old"
        decorated_function = (dec(0, message, logger=logger)(test_func))

        decorated_function(arg1="Testuser", arg2=16)

        logger.log.assert_called_once_with(0, "Hello world. My name is Testuser"
                                              ", I am 16 old")

    def test_message_formatting_result(self):
        dec = LoggingDecorator(log_after_execution=True)
        logger = Mock()
        message = "{result:s}"
        function = Mock(return_value="asdasdasd")
        decorated_function = (dec(0, message, logger=logger)(function))

        decorated_function()

        logger.log.assert_called_once_with(0, "asdasdasd")

    def test_message_formatting_exception(self):
        dec = LoggingDecorator(log_on_exception=True)
        MyExc = type("MyExc", (Exception,), {"myvar": "myvar"})
        logger = Mock()
        message = "{e.myvar:s}"
        function = Mock(side_effect=MyExc())
        decorated_function = (dec(0, message, logger=logger,
                                  reraise=False, on_exceptions=[MyExc])
                              (function))

        decorated_function()

        logger.log.assert_called_once_with(0, "myvar")
