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

class ExceptionGroupParser:
    # Some elements are static, the simplest (and probably fastest) way
    # is to just compare them.
    _eg_header = '+ Exception Group Traceback (most recent call last):'
    _eg_prefix = '| '
    _eg_traceback_prefix = '|   '
    _eg_nesting_sep = '+-+----------------'
    _eg_unnesting_sep = '+------------------------------------'
    _eg_exc_header = '| Traceback (most recent call last):'
    _eg_exc_sep = '+---------------- '
    _dotall = '...'

    class _Done(Exception):
        """Raised when parser is finised."""

    def __init__(self, text):
        self._text_lines = text.split('\n')
        self._line = 0
        self._indent_level = 0
        self._result = []

    def parse(self):
        self._visit_exception_group()
        # Now, to nested exceptions:
        while True:
            self._visit_traceback()
            try:
                self._visit_message()
            except self._Done:
                break
        return self._result

    def _visit_exception_group(self):
        # ExceptionGroup consists of a header
        # and traceback lines (which we don't care about)
        if self._current_line != self._indent(self._eg_header):
            self._fail("ExceptionGroup header is not found")
        self._go_to_next_line()
        # Now, skip all the following exception traceback:
        self._visit_traceback(is_exception_group=True)

    def _visit_traceback(self, *, is_exception_group=False):
        # traceback might be missing,
        # it might be in a format of `File "<string>", line 2, in f`
        # it might be just `...`, as doctest documents

        # We start count from `1` for `while` to work with `True`:
        counter = itertools.count(1)
        while (iteration := next(counter)):
            # We just skip these lines, they don't have any real value
            current = self._current_line
            print('_visit_traceback', current)

            # It might be an exception's traceback header:
            if current == self._indent(self._eg_exc_header):
                self._go_to_next_line()
                continue

            # It might be just a regular traceback:
            if current.startswith(self._indent(self._eg_traceback_prefix)):
                if not is_exception_group and iteration == 1:
                    return self._visit_syntax_error()
                self._go_to_next_line()
                continue

            # Handle `...` special case. It can be: `|...`, `| ...`, `| ...`, etc.
            if current.startswith(self._indent(self._eg_prefix)):
                replaced = current.replace(
                   self._indent(self._eg_prefix), '',
                ).strip()
                if replaced == self._dotall:
                   self._go_to_next_line()

            break

    def _visit_message(self):
        # Messages might be multiline or contain notes
        counter = itertools.count(1)
        while (iteration := next(counter)):
            current = self._current_line
            print('_visit_message  ', current)
            if not current.startswith(self._indent(self._eg_prefix)):
                if iteration == 1:
                    self._fail("ExceptionGroup must have at least one message")
                return

            self._add_result(current)
            self._go_to_next_line()
            if self._maybe_move_further():
                return

    def _visit_syntax_error(self):
        while True:
            print('_visit_syntax_err', self._current_line)
            if self._current_line.startswith(
                self._indent(self._eg_traceback_prefix),
            ):
                self._add_result(self._current_line, is_syntax_eror=True)
                self._go_to_next_line()
                continue
            break

    # Helpers:

    def _fail(self, msg):
        raise ValueError(msg, self._result)

    def _add_result(self, line, *, is_syntax_eror=False):
        line = line.replace(self._eg_prefix, '', 1)
        if is_syntax_eror:
            # SyntaxError format is special, only remove a single space.
            line = line.replace(' ', '', 1)
        else:
            # `format_exception_only` uses different indent format,
            # it is 3-based, so we need to reindent this value.
            line = line.lstrip()
            line = ' ' * self._indent_level * 3 + line
        if not line.endswith('\n'):
            line += '\n'
        self._result.append(line)

    def _go_to_next_line(self):
        self._line += 1

    def _maybe_move_further(self):
        if self._line >= len(self._text_lines) - 1:
            raise self._Done

        if self._current_line.startswith(self._indent(self._eg_nesting_sep)):
            self._indent_level += 1
            self._go_to_next_line()
            self._maybe_move_further()
            return True
        elif self._current_line.startswith(self._indent(self._eg_unnesting_sep)):
            self._indent_level -= 1
            self._go_to_next_line()
            self._maybe_move_further()
            return True
        elif self._current_line.startswith(self._indent(self._eg_exc_sep)):
            self._go_to_next_line()
            self._maybe_move_further()
            return True
        return False

    @property
    def _current_line(self):
        return self._text_lines[self._line]

    def _indent(self, other):
        return '  ' * (self._indent_level + 1) + other

x = ExceptionGroupParser(text[1:]).parse()
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
