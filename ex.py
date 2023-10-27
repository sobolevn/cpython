def test_syntax_error_with_note(cls, multiline=False):
    """
    >>> test_syntax_error_with_note(TabError, multiline=True)
    Traceback (most recent call last):
      ...
    TabError: Two
    error lines
    Note
    Line
    """
    exc = cls(
        "Two\nerror lines" if multiline else "error",
        ("x.py", 23, None, "bad syntax"),
    )
    exc.add_note('Note\nLine' if multiline else 'Note')
    raise exc
