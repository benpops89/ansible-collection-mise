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

Ensures all tools specified in mise.toml are installed. Runs `mise install` to install any missing tools from the config.

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

Add or remove tools from mise.toml configuration.

#### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| tools | list | required | List of tools (e.g., `["node@20", "python@3.11"]`). |
| state | string | present | `present` to add to config, `absent` to remove from config. |
| global | bool | false | Use global mise.toml instead of local. |

#### Return Values

| Key | Type | Description |
|-----|------|-------------|
| changed | bool | Whether any changes were made. |
| msg | string | Output message from the operation. |

#### Examples

```yaml
# Add tools to config (installs and adds to mise.toml)
- name: Add Node.js and Python to config
  benpops89.mise.mise_tool:
    tools:
      - node@20
      - python@3.11
    state: present

# Add tools to global config
- name: Add tools to global config
  benpops89.mise.mise_tool:
    tools:
      - node@20
    global: true

# Remove tools from config (uninstalls and removes from mise.toml)
- name: Remove Node.js from config
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
