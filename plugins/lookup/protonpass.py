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
        description: Title of the item in the Proton Pass vault.
        required: true
        type: string
      vault:
        description: Name of the vault containing the item.
        required: true
        type: string
      field:
        description: Field name to retrieve from the item (e.g. C(password), C(username)).
        required: false
        type: string
      totp:
        description: Set to C(true) to retrieve the TOTP/2FA code instead of a field value.
        required: false
        type: bool
    notes:
      - Exactly one of C(field) or C(totp) must be specified.
      - The user must authenticate via C(pass-cli login) before using this plugin.
      - Item titles containing spaces are supported.
"""

EXAMPLES = """
- name: Retrieve a password field
  ansible.builtin.set_fact:
    db_password: "{{ lookup('c01110011.protonpass.protonpass', 'My Database', vault='Personal', field='password') }}"

- name: Retrieve a TOTP code
  ansible.builtin.set_fact:
    otp: "{{ lookup('c01110011.protonpass.protonpass', 'My Service', vault='Work', totp=true) }}"

- name: Use directly in a task
  ansible.builtin.debug:
    msg: "{{ lookup('c01110011.protonpass.protonpass', 'My Secret', vault='Personal', field='password') }}"
"""

RETURN = """
_list:
  description: Single-element list containing the retrieved value.
  type: list
  elements: string
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
