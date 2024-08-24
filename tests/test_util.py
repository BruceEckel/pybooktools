from pybooktools.util import FileChanged


def test_init():
    assert not FileChanged("sample").modified


def test_true_method():
    file_changed = FileChanged("sample")
    file_changed.true()
    assert file_changed.modified


def test_false_method():
    file_changed = FileChanged("sample")
    file_changed.false()
    assert not file_changed.modified


def test_report_modified_true():
    file_changed = FileChanged("sample")
    modified_report = file_changed.true().report()
    assert modified_report == "[bold red]sample[/bold red]"


def test_report_modified_false():
    file_changed = FileChanged("sample")
    non_modified_report = file_changed.false().report()
    assert non_modified_report == "[bold green]sample[/bold green]"
