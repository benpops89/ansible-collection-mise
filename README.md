# Ansible Collection: community.mise

Ansible collection for managing [mise](https://mise.jdx.dev/) tools.

## Requirements

- Ansible 2.9+
- mise must be installed on the target host

## Installation

Install the collection from Ansible Galaxy:

```bash
ansible-galaxy collection install community.mise
```

## Modules

### mise_sync

Ensures mise tools are in sync (installed or uninstalled) based on the mise.toml configuration.

#### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| path | path | null | Path to `.mise.toml` file. Defaults to current directory. |
| global | bool | false | Use global mise.toml instead of local. |
| trust | bool | false | Trust the mise.toml config before running commands. |
| state | string | present | `present` to install, `absent` to uninstall. |

#### Return Values

| Key | Type | Description |
|-----|------|-------------|
| changed | bool | Whether any changes were made. |
| missing_tools | list | Tools that were missing (before install). |
| installed_tools | list | Tools that are/were installed. |

#### Examples

```yaml
# Ensure all mise tools are installed
- name: Ensure mise tools are installed
  community.mise.mise_sync:

# Ensure global mise tools are installed
- name: Ensure global mise tools are installed
  community.mise.mise_sync:
    global: true

# Trust config and ensure mise tools are installed
- name: Ensure mise tools are installed (auto-trust config)
  community.mise.mise_sync:
    path: /path/to/mise.toml
    trust: true

# Trust global config and ensure mise tools are installed
- name: Ensure global mise tools are installed (auto-trust config)
  community.mise.mise_sync:
    global: true
    trust: true

# Uninstall all mise tools
- name: Remove all mise tools
  community.mise.mise_sync:
    state: absent
```

## Development

### Running Tests

```bash
# Unit tests
pytest tests/unit/

# Integration tests
ansible-playbook tests/integration/
```

## License

GPL-3.0-or-later

## Author

Ben Poppy (@benpops89)
