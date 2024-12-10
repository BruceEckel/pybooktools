from pprint import pformat

from icecream import ic


def ocl_output(*args) -> str:
    lines: list[str] = []
    for arg in args:
        if isinstance(arg, str):
            # Handle strings without adding quotes or parentheses
            lines.extend([f"#| {line}" for line in arg.splitlines()])
        else:
            # Format non-string arguments with pprint
            formatted = pformat(arg, width=47)
            lines.extend(
                [f"#| {line.strip()}" for line in formatted.splitlines()]
            )
    ic(lines)
    return "\n".join(lines)


t_1 = 1
t_2 = "foo"
t_3 = "A really long line that just keeps going am I finished yet? Yes!"

for input_arg in [t_1, t_2, t_3]:
    ic(ocl_output(input_arg))

ic(ocl_output(t_1, t_2, t_3))
