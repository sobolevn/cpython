def raise_group():
    """
    >>> raise_group()
    Exception Group Traceback (most recent call last):
    ...
    ExceptionGroup: A (2 sub-exceptions)
    ...
    TypeError: 1
    ...
    ValueError: 2
    """
    raise ExceptionGroup('A', [TypeError(1), ValueError(2)])
