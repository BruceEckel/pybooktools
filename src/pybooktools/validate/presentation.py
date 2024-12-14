# presentation.py


def report(test: bool, case_id: int) -> str:
    if test:
        return "\n" + f" Case {case_id} passed ".center(47, "=")
    else:
        return f" Case {case_id} failed ".center(47, "=")


passed = lambda case_id: report(True, case_id)
failed = lambda case_id: report(False, case_id)
