#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: mise_tool
short_description: Install or uninstall specific mise tools
description:
    - Install or uninstall specific tools from mise.
    - Tools are specified as a list (e.g., ["node@20", "python@3.11"]).
version_added: "0.1.0"
author:
    - Ben Poppy (@benpops89)
options:
    tools:
        description:
            - List of tools to install or uninstall.
            - Format: tool@version (e.g., "node@20", "python@3.11").
        type: list
        elements: str
        required: true
    state:
        description:
            - Desired state of the tools.
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
      - python@3.11
    state: present
    global: true

# Uninstall specific tools
- name: Remove Node.js
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


def install_tools(module, tools):
    if not tools:
        return False, "No tools to install"

    result = run_mise_command(module, ["install"] + tools)
    return True, f"Installed tools: {', '.join(tools)}"


def uninstall_tools(module, tools):
    if not tools:
        return False, "No tools to uninstall"

    result = run_mise_command(module, ["uninstall"] + tools)
    return True, f"Uninstalled tools: {', '.join(tools)}"


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
        changed, msg = install_tools(module, tools)
    else:
        changed, msg = uninstall_tools(module, tools)

    module.exit_json(
        changed=changed,
        msg=msg,
    )


def main():
    run_module()


if __name__ == "__main__":
    main()
