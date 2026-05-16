# c01110011.protonpass

Ansible lookup plugin for retrieving secrets from [Proton Pass](https://proton.me/pass) vaults
using the official [pass-cli](https://github.com/protonpass/pass-cli).

## Requirements

- Ansible Core >= 2.16
- [pass-cli](https://github.com/protonpass/pass-cli) installed and authenticated

Install and authenticate pass-cli before running any playbooks:

```bash
pass-cli login
```

## Installation

```bash
ansible-galaxy collection install c01110011.protonpass
```

Or add to `requirements.yml`:

```yaml
collections:
  - name: c01110011.protonpass
```

To pin a specific version:

```bash
ansible-galaxy collection install c01110011.protonpass:==1.0.0
```

To upgrade:

```bash
ansible-galaxy collection install c01110011.protonpass --upgrade
```

## Usage

### Retrieve a field value

```yaml
- name: Get database password
  ansible.builtin.set_fact:
    db_password: "{{ lookup('c01110011.protonpass.protonpass', 'My Database', vault='Personal', field='password') }}"
```

### Retrieve a TOTP code

```yaml
- name: Get TOTP code
  ansible.builtin.set_fact:
    otp: "{{ lookup('c01110011.protonpass.protonpass', 'My Service', vault='Work', totp=true) }}"
```

### Use directly in a task

```yaml
- name: Configure application
  ansible.builtin.template:
    src: config.j2
    dest: /etc/app/config.yml
  vars:
    api_key: "{{ lookup('c01110011.protonpass.protonpass', 'App API Key', vault='Work', field='password') }}"
```

## Parameters

| Parameter | Required | Type | Description |
|-----------|----------|------|-------------|
| `_terms` | yes | string | Title of the item in Proton Pass |
| `vault` | yes | string | Name of the vault containing the item |
| `field` | no* | string | Field name to retrieve (e.g. `password`, `username`) |
| `totp` | no* | bool | Set to `true` to retrieve the TOTP/2FA code |

\* Exactly one of `field` or `totp` must be specified.

## Release Notes

See the [changelog](https://github.com/c01110011/ansible-collection-protonpass/blob/main/c01110011/protonpass/CHANGELOG.rst).

## License

GNU General Public License v3.0 or later. See [LICENSE](https://www.gnu.org/licenses/gpl-3.0.txt).
