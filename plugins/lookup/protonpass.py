from __future__ import annotations

from typing import Any

from ansible.errors import AnsibleError
from ansible.utils.display import Display
from ansible.plugins.lookup import LookupBase

import subprocess

# Author: Catalin Stan (@c01110011)
# Copyright 2026
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

DOCUMENTATION = """
    name: protonpass
    author: Catalin Stan (@c01110011)
    version_added: "1.0.0"
    short_description: Retrieve secrets from Proton Pass vaults.
    description:
      - Retrieves secrets from Proton Pass vaults using the official pass-cli.
      - Requires pass-cli to be installed and authenticated via C(pass-cli login).
    options:
      _terms:
        description: Terms to lookup
        required: True
    notes:
      - The user must authenticate via C(pass-cli login) before using this plugin.
      - Item titles containing spaces are supported.
"""

EXAMPLES = """
- name: Example usage of protonpass
  ansible.builtin.debug:
    msg: "{{ lookup('protonpass', 'example_term') }}"
"""

RETURN = """
_list:
  description: The list of values found by the lookup
  type: list
"""

display = Display()

class LookupModule(LookupBase):

    def run(
        self,
        terms: list[str],
        variables: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> list[str]:
        display.vvv(f"Running protonpass lookup plugin with terms: {terms}")

        if not terms:
            raise AnsibleError("Terms must be specified.")

        item_title = terms[0]
        field = kwargs.get('field')
        vault = kwargs.get('vault')
        totp = kwargs.get('totp')

        if field is None and totp is None:
            raise AnsibleError("The 'field' or 'totp' parameters must be specified.")

        if field is not None and totp is not None:
            raise AnsibleError("The 'field' and 'totp' parameters cannot be specified at the same time.")

        if vault is None:
            raise AnsibleError("The 'vault' parameter is required.")

        command = ["pass-cli", "item"]

        if totp is not None:
            command.extend(["totp"])

        if field is not None:
            command.extend(["view", "--field", field])

        command.extend(["--item-title", item_title, "--vault-name", vault])

        try:
            output = subprocess.run(command, capture_output=True, text=True, check=True)
        except FileNotFoundError:
            raise AnsibleError("The 'pass-cli' executable could not be found.")
        except subprocess.CalledProcessError as e:
            display.error(e.stderr.strip())
            raise AnsibleError(f"Process Error {format(e)}")

        return [output.stdout.strip()]
