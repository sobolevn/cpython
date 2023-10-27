import re

_EXCEPTION_GROUP_RE = re.compile(r"""
        # at first, we need to know the current identation
        ^(?P<indent1>\s+ )
        # at the same line it has the traceback information
        (?P<n> Traceback\ \( most\ recent\ call\ last \): \s*)
        # next, consume all traceback lines
        ^(?P<stack> \1 \s{2} .*?)
        # stop when the same indentation is found, followed by alpha-numeric
        ^(?P<msg> \1 \w+ .*?)
        # this is the line splitter
        ^\1\+-[\+-]--------------

(?:\+-[\+-]--------------)(?:.*)
^(?P<single>\s+ \w+ .*)
(?:\+-[\+-]--------------)
""", re.VERBOSE | re.MULTILINE | re.DOTALL)

text = """
    Traceback (most recent call last):
      File "<stdin>", line 3, in <module>
      File "<stdin>", line 2, in f
    TypeError: 1
    Happened in Iteration 1
    +---------------- 2 ----------------
    ValueError: 2
    +---------------- 3 ----------------
    ExceptionGroup: B (2 sub-exceptions)
    +-+---------------- 1 ----------------
      IndexError: 3
      +---------------- 2 ----------------
      IndexError: 4
      +------------------------------------
"""

text = text[1:]
print(text)
print('--')
m = _EXCEPTION_GROUP_RE.findall(text)
print(m)
