# Ansible Collection: benpops89.mise

Ansible collection for managing [mise](https://mise.jdx.dev/) tools.

## Requirements

- Ansible 2.9+
- mise must be installed on the target host

## Installation

Install from GitHub:

```bash
ansible-galaxy collection install git+https://github.com/benpops89/ansible-collection-mise.git
```

## Modules

### mise_sync

Ensures all tools specified in mise.toml are installed.

#### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| path | path | null | Path to `.mise.toml` file. Defaults to current directory. |
| global | bool | false | Use global mise.toml instead of local. |
| trust | bool | false | Trust the mise.toml config before running commands. |

#### Return Values

| Key | Type | Description |
|-----|------|-------------|
| changed | bool | Whether any changes were made. |
| missing_tools | list | Tools that were missing (before install). |
| installed_tools | list | Tools that are installed. |

#### Examples

```yaml
# Ensure all mise tools are installed
- name: Ensure mise tools are installed
  benpops89.mise.mise_sync:

# Ensure global mise tools are installed
- name: Ensure global mise tools are installed
  benpops89.mise.mise_sync:
    global: true

# Trust config and ensure mise tools are installed
- name: Ensure mise tools are installed (auto-trust config)
  benpops89.mise.mise_sync:
    path: /path/to/mise.toml
    trust: true
```

### mise_tool

Install or uninstall specific tools.

#### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| tools | list | required | List of tools (e.g., `["node@20", "python@3.11"]`). |
| state | string | present | `present` to install, `absent` to uninstall. |
| global | bool | false | Use global mise.toml instead of local. |

#### Return Values

| Key | Type | Description |
|-----|------|-------------|
| changed | bool | Whether any changes were made. |
| msg | string | Output message from the operation. |

#### Examples

```yaml
# Install specific tools
- name: Install Node.js and Python
  benpops89.mise.mise_tool:
    tools:
      - node@20
      - python@3.11
    state: present

# Install tools globally
- name: Install tools globally
  benpops89.mise.mise_tool:
    tools:
      - node@20
    global: true

# Uninstall specific tools
- name: Remove Node.js
  benpops89.mise.mise_tool:
    tools:
      - node@20
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

MIT

## Author

Ben Poppy (@benpops89)
