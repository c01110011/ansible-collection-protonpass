from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from ansible.errors import AnsibleError

_LOOKUP_DIR = Path(__file__).parents[4] / "plugins" / "lookup"
if str(_LOOKUP_DIR) not in sys.path:
    sys.path.insert(0, str(_LOOKUP_DIR))

from protonpass import LookupModule  # noqa: E402


def _completed(stdout: str) -> MagicMock:
    result = MagicMock()
    result.stdout = stdout
    return result


@pytest.fixture
def lookup() -> LookupModule:
    return LookupModule()


class TestProtonpassLookupValidation:
    def test_raises_when_neither_field_nor_totp_provided(self, lookup: LookupModule) -> None:
        with pytest.raises(AnsibleError):
            lookup.run(["My Item"], vault="test-vault")

    def test_raises_when_both_field_and_totp_provided(self, lookup: LookupModule) -> None:
        with pytest.raises(AnsibleError):
            lookup.run(["My Item"], vault="test-vault", field="password", totp=True)

    def test_raises_when_terms_is_empty(self, lookup: LookupModule) -> None:
        with pytest.raises(AnsibleError):
            lookup.run([], vault="test-vault", field="password")

    def test_raises_when_vault_not_provided(self, lookup: LookupModule) -> None:
        with pytest.raises(AnsibleError):
            lookup.run(["My Item"], field="password")

    def test_raises_when_field_is_empty_string(self, lookup: LookupModule) -> None:
        with pytest.raises(AnsibleError):
            lookup.run(["My Item"], vault="test-vault", field="")


class TestProtonpassLookupFieldRetrieval:
    def test_calls_pass_cli_with_item_title_and_field(self, lookup: LookupModule) -> None:
        with patch("protonpass.subprocess.run", return_value=_completed("secret")) as mock_run:
            lookup.run(["My Item"], vault="test-vault", field="password")
        cmd = mock_run.call_args[0][0]
        assert "pass-cli" in cmd
        assert "--item-title" in cmd
        assert "My Item" in cmd
        assert "--field" in cmd
        assert "password" in cmd

    def test_calls_pass_cli_with_vault_when_provided(self, lookup: LookupModule) -> None:
        with patch("protonpass.subprocess.run", return_value=_completed("secret")) as mock_run:
            lookup.run(["My Item"], vault="test-vault", field="password")
        cmd = mock_run.call_args[0][0]
        assert "--vault-name" in cmd
        assert "test-vault" in cmd

    def test_returns_field_value_as_single_element_list(self, lookup: LookupModule) -> None:
        with patch("protonpass.subprocess.run", return_value=_completed("mysecret\n")):
            result = lookup.run(["My Item"], vault="test-vault", field="password")
        assert result == ["mysecret"]

    def test_raises_on_pass_cli_not_found(self, lookup: LookupModule) -> None:
        with patch("protonpass.subprocess.run", side_effect=FileNotFoundError):
            with pytest.raises(AnsibleError, match="pass-cli"):
                lookup.run(["My Item"], vault="test-vault", field="password")

    def test_raises_on_nonzero_exit_code(self, lookup: LookupModule) -> None:
        error = subprocess.CalledProcessError(1, "pass-cli", stderr="item not found")
        with patch("protonpass.subprocess.run", side_effect=error):
            with pytest.raises(AnsibleError):
                lookup.run(["My Item"], vault="test-vault", field="password")


class TestProtonpassLookupTotp:
    def test_calls_pass_cli_totp_command(self, lookup: LookupModule) -> None:
        with patch("protonpass.subprocess.run", return_value=_completed("123456")) as mock_run:
            lookup.run(["My Item"], vault="test-vault", totp=True)
        cmd = mock_run.call_args[0][0]
        assert "totp" in cmd

    def test_returns_totp_value_as_single_element_list(self, lookup: LookupModule) -> None:
        with patch("protonpass.subprocess.run", return_value=_completed("123456\n")):
            result = lookup.run(["My Item"], vault="test-vault", totp=True)
        assert result == ["123456"]
