from dataclasses import dataclass

from rich.columns import Columns
from rich.console import Console
from rich.panel import Panel


@dataclass
class Comparator:
    actual_output: str
    expected_output: str
    actual_output_written: bool = False

    def compare(self) -> None:
        """
        Compares actual output with expected output and displays a detailed
        and visually appealing result using Rich library. Actual output is
        displayed in a green panel, and expected output in a blue panel.
        """
        console = Console()

        # Check if the actual output has been written
        if not self.actual_output_written:
            console.print(
                f"[bold red]Error:[/bold red] Actual output not written in {self}"
            )
            return

        # Create panels for actual and expected output
        actual_panel = Panel(
            self.actual_output,
            title="Actual Output",
            title_align="center",
            border_style="bold green",
        )
        expected_panel = Panel(
            self.expected_output,
            title="Expected Output",
            title_align="center",
            border_style="bold blue",
        )

        # Display panels side by side using Columns
        if self.actual_output != self.expected_output:
            console.print(Columns([actual_panel, expected_panel]))
        else:
            # If match, show both panels with additional indication of match success
            match_message = Panel(
                "[bold green]Outputs Match![/bold green]",
                title="Result",
                title_align="center",
                border_style="green",
            )
            console.print(Columns([actual_panel, expected_panel]))
            console.print(match_message)


# Example usage
if __name__ == "__main__":
    # Example cases
    comparator_1 = Comparator(
        actual_output="Hello World",
        expected_output="Hello World",
        actual_output_written=True,
    )
    comparator_2 = Comparator(
        actual_output="Hello World",
        expected_output="Hello Universe",
        actual_output_written=True,
    )
    comparator_3 = Comparator(
        actual_output="Foo", expected_output="Bar", actual_output_written=False
    )

    comparator_1.compare()  # Should indicate a match
    comparator_2.compare()  # Should indicate a mismatch
    comparator_3.compare()  # Should indicate an error
