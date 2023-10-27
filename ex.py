def f():
    exc = TypeError(1)
    exc.add_note('Happened in Iteration 1')
    raise exc

def test_syntax_error_with_note():
    """
    >>> test_syntax_error_with_note()
    + Exception Group Traceback (most recent call last):
    |   File "/Users/sobolev/Desktop/cpython/ex.py", line 49, in <module>
    |     test_syntax_error_with_note()
    |   File "/Users/sobolev/Desktop/cpython/ex.py", line 40, in test_syntax_error_with_note
    |     raise ExceptionGroup('AB', [
    | ExceptionGroup: A
    | B (5 sub-exceptions)
    +-+---------------- 1 ----------------
      | Traceback (most recent call last):
      |   File "/Users/sobolev/Desktop/cpython/ex.py", line 37, in test_syntax_error_with_note
      |     f()
      |   File "/Users/sobolev/Desktop/cpython/ex.py", line 4, in f
      |     raise exc
      | TypeError: 1
      | Happened in Iteration 1
      +---------------- 2 ----------------
      | ValueError: x
      | y
      +---------------- 3 ----------------
      | ExceptionGroup: B (2 sub-exceptions)
      +-+---------------- 1 ----------------
        | IndexError: 3
        +---------------- 2 ----------------
        | IndexError: 4
        +------------------------------------
      +---------------- 4 ----------------
      | IndexError: 5
      +---------------- 5 ----------------
      |   File "x.py", line 23
      |     bad syntax
      | SyntaxError: error
      +------------------------------------

    """
    try:
        f()
    except TypeError as e:
        exc = e
    raise ExceptionGroup('A\nB', [
        exc,
        ValueError("x\ny"),
        ExceptionGroup('B', [IndexError(3), IndexError(4)]),
        IndexError(5),
        SyntaxError("error", ("x.py", 23, None, "bad syntax")),
    ])

if __name__ == '__main__':
    test_syntax_error_with_note()
