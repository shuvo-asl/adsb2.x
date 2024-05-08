# Pytest
## 2024-03-3

Today I have cover the following items:

* Install pytest
* Trying to understand how pytest is working.
* Cover some awesome pytest features like: **pytest.raises, -q, write test case within a class**,

### pytest.raises

This line is checked the context manager of the pytest it raised the any exception or not which is defined inside the raises(). If raise the exception  the it passed otherwise it's failed. For example:

        def test_mytest():
            with pytest.raises(
                SystemExit
            ):
                raise_system_exit_exception()

### pytest -q

When the -q option is used, pytest will only print a summary of the test results, including the number of tests that passed, failed, and were skipped. It will also print any errors or warnings that occurred during the test run.

### Class

    import pytest
    from helper.helper_test import *

    class TestSample:
        """
            This class is responsible to handle all of 
            The sample test cases.
        """

        def test_addition_success(self):
            result = sum(10,5)
            assert result == 15
        
        def test_check_json_data_success(self):
            data = {
                "name" : "Shuvo",
                "designation": "Senior Software Engineer"
            }
            result = check_json_data(data)
            assert result == "OK"
        

        def test_check_json_data_failed(self):
            data = [10,2,3]
            with pytest.raises(Exception):
                check_json_data(data)        