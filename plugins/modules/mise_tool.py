#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: mise_tool
short_description: Add or remove mise tools from config
description:
    - Add or remove tools from mise.toml configuration.
    - Uses 'mise use' to add tools (installs and adds to config).
    - Uses 'mise use --remove' to remove tools (uninstalls and removes from config).
version_added: "0.1.0"
author:
    - Ben Poppy (@benpops89)
options:
    tools:
        description:
            - List of tools to add or remove.
            - Format: tool@version (e.g., "node@20", "python@3.11").
        type: list
        elements: str
        required: true
    state:
        description:
            - 'present' to add tools to config, 'absent' to remove tools from config.
        type: str
        choices: [present, absent]
        default: present
    global:
        description:
            - Use the global mise.toml configuration instead of local.
        type: bool
        default: false
notes:
    - mise must be installed on the target host.
    - This module requires mise to be in PATH.
"""

EXAMPLES = r"""
# Add tools to config and install
- name: Add Node.js and Python to config
  benpops89.mise.mise_tool:
    tools:
      - node@20
      - python@3.11
    state: present

# Add tools globally
- name: Add tools to global config
  benpops89.mise.mise_tool:
    tools:
      - node@20
    global: true

# Remove tools from config
- name: Remove Node.js from config
  benpops89.mise.mise_tool:
    tools:
      - node@20
    state: absent
"""

RETURN = r"""
changed:
    description: Whether any changes were made.
    type: bool
    returned: always
msg:
    description: Output message from the operation.
    type: str
    returned: always
"""

from ansible.module_utils.basic import AnsibleModule
import subprocess


def run_mise_command(module, args, check=True):
    cmd = ["mise"] + args

    if module.params.get("global"):
        cmd.append("--global")

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        check=False,
    )

    if check and result.returncode != 0:
        module.fail_json(
            msg=f"mise command failed: {' '.join(cmd)}",
            stderr=result.stderr,
            stdout=result.stdout,
        )

    return result


def add_tools(module, tools):
    if not tools:
        return False, "No tools to add"

    result = run_mise_command(module, ["use"] + tools)
    return True, f"Added tools to config: {', '.join(tools)}"


def remove_tools(module, tools):
    if not tools:
        return False, "No tools to remove"

    result = run_mise_command(module, ["unuse", "--yes"] + tools)
    return True, f"Removed tools from config: {', '.join(tools)}"


def run_module():
    module_args = dict(
        tools=dict(type="list", elements="str", required=True),
        state=dict(type="str", required=False, default="present", choices=["present", "absent"]),
        **{"global": dict(type="bool", required=False, default=False)},
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True,
    )

    tools = module.params.get("tools")
    state = module.params.get("state")

    if state == "present":
        changed, msg = add_tools(module, tools)
    else:
        changed, msg = remove_tools(module, tools)

    module.exit_json(
        changed=changed,
        msg=msg,
    )


def main():
    run_module()


if __name__ == "__main__":
    main()
