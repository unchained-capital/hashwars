from test.base import *

class TestDuration():
    
    def test_requires_correctly_ordered_start_and_end(self):
        with raises(AssertionError, match="(?i)first parameter.+should be less than second parameter"):
            Duration(2,1)

    def test_length(self):
        assert Duration(1,2).length == 1
        assert Duration(1.3,2).length == 0.7
        assert Duration(0,0.1).length == 0.1
        assert Duration(-1,2).length == 3

    def test_contains(self):
        assert Duration(1,2).contains(1.5)
        assert Duration(1,2).contains(1)
        assert not Duration(1,2).contains(2.5)

    def test_random_time(self):
        assert 1 <  Duration(1,2).random_time()  < 2
