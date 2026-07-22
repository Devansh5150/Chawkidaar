from typer.testing import CliRunner

from chawkidaar.main import app

runner = CliRunner()


def test_status():
    result = runner.invoke(app, ["status"])
    assert result.exit_code == 0
    assert "Chawkidaar is active" in result.stdout


def test_doctor():
    result = runner.invoke(app, ["doctor"])
    assert result.exit_code == 0
    assert "System Diagnostics" in result.stdout
    assert "Python Version" in result.stdout
