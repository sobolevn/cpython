e = SyntaxError("error", ("x.py", 23, None, "bad syntax"))
raise ExceptionGroup('A', [e])
