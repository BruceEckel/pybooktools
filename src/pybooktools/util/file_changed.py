from dataclasses import dataclass, field


@dataclass
class FileChanged:
    file_name: str
    # Set to False and exclude field from constructor arguments
    modified: bool = field(default=False, init=False)

    def true(self) -> "FileChanged":
        self.modified = True
        return self

    def false(self) -> "FileChanged":
        self.modified = False
        return self

    def report(self) -> str:
        if self.modified:
            return f"[bold red]{self.file_name}[/bold red]"
        return f"[bold green]{self.file_name}[/bold green]"
