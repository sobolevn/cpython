text = """
  + Exception Group Traceback (most recent call last):
  |   File "<stdin>", line 1, in <module>
  | ExceptionGroup: A (5 sub-exceptions)
  +-+---------------- 1 ----------------
    | Traceback (most recent call last):
    |   File "<stdin>", line 3, in <module>
    |   File "<stdin>", line 2, in f
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

import itertools



x = _ExceptionGroupParser(text[1:]).parse()
print("".join(x))


def f():
    exc = TypeError(1)
    exc.add_note('Happened in Iteration 1')
    raise exc

def raise_exc():
    try:
        f()
    except TypeError as e:
        exc = e
    return ExceptionGroup('A\nB', [
        # exc,
        ValueError("x\ny"),
        # ExceptionGroup('B', [IndexError(3), IndexError(4)]),
        # IndexError(5),
        # SyntaxError("error", ("x.py", 23, None, "bad syntax")),
    ])

import traceback
y = traceback.format_exception_only(raise_exc(), show_group=True)
print(y)
print("".join(y))
print('----')
# for i in range(len(x)):
#     print(x[i])
#     print(y[i])
#     print(x[i] == y[i])
print('res', "".join(x) == "".join(y))
