#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: mise_sync
short_description: Manage mise tool installations
description:
    - Syncs mise tools by installing missing tools or uninstalling existing tools based on mise.toml configuration.
version_added: "0.1.0"
author:
    - Ben Poppy (@benpops89)
options:
    path:
        description:
            - Path to the mise.toml file.
            - If not specified, the current directory is used.
        type: path
    global:
        description:
            - Use the global mise.toml configuration instead of local.
        type: bool
        default: false
    trust:
        description:
            - Trust the mise.toml config file before running commands.
            - Required when running against a new config that hasn't been trusted.
        type: bool
        default: false
    state:
        description:
            - Desired state of the tool.
        type: str
        choices: [present, absent]
        default: present
notes:
    - mise must be installed on the target host.
    - This module requires mise to be in PATH.
"""

EXAMPLES = r"""
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
"""

RETURN = r"""
changed:
    description: Whether any changes were made.
    type: bool
    returned: always
missing_tools:
    description: Tools that were missing (before install).
    type: list
    returned: when state=present
installed_tools:
    description: Tools that are/were installed.
    type: list
    returned: always
"""

from ansible.module_utils.basic import AnsibleModule
import json
import os
import subprocess


def run_mise_command(module, args, check=True, env=None, cwd=None):
    cmd = ["mise"] + args

    cmd_env = os.environ.copy()
    if env:
        cmd_env.update(env)

    if module.params.get("global"):
        cmd.append("--global")

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        check=False,
        env=cmd_env,
        cwd=cwd,
    )

    if check and result.returncode != 0:
        module.fail_json(
            msg=f"mise command failed: {' '.join(cmd)}",
            stderr=result.stderr,
            stdout=result.stdout,
        )

    return result


def trust_config(module):
    if not module.params.get("trust"):
        return

    path = module.params.get("path")
    global_flag = module.params.get("global")

    if path:
        config_dir = os.path.dirname(os.path.abspath(path))
        if config_dir:
            result = run_mise_command(module, ["trust", config_dir], check=True)
            return
    
    if global_flag:
        result = run_mise_command(module, ["config", "get", "MISE_GLOBAL_CONFIG_FILE"], check=False)
        if result.returncode == 0 and result.stdout.strip():
            global_config = result.stdout.strip()
            trusted_paths = os.environ.get("MISE_TRUSTED_CONFIG_PATHS", "")
            if global_config not in trusted_paths:
                new_trusted = f"{trusted_paths}:{global_config}" if trusted_paths else global_config
                run_mise_command(
                    module, 
                    ["trust", global_config], 
                    check=True, 
                    env={"MISE_TRUSTED_CONFIG_PATHS": new_trusted}
                )
            return


def get_tools_state(module):
    path = module.params.get("path")
    global_flag = module.params.get("global")
    cwd = None
    
    if path:
        config_dir = os.path.dirname(os.path.abspath(path))
        if config_dir:
            cwd = config_dir

    cmd = ["ls", "--json"]
    result = run_mise_command(module, cmd, check=False, cwd=cwd)

    if result.returncode != 0:
        if "no tools found" in result.stderr.lower() or result.stdout.strip() == "":
            return {}
        module.fail_json(
            msg="Failed to get mise tools state",
            stderr=result.stderr,
            stdout=result.stdout,
        )

    try:
        tools = json.loads(result.stdout)
    except json.JSONDecodeError as e:
        module.fail_json(
            msg=f"Failed to parse mise ls output: {e}", stdout=result.stdout
        )

    # Filter tools to only include those from the specified config file
    config_path = None
    if path:
        config_path = os.path.abspath(path)
    elif global_flag:
        # Get the global config path
        result = run_mise_command(module, ["config", "get", "MISE_GLOBAL_CONFIG_FILE"], check=False)
        if result.returncode == 0 and result.stdout.strip():
            config_path = result.stdout.strip()
    
    if config_path:
        tools = filter_tools_by_config(tools, config_path)

    return tools


def filter_tools_by_config(tools, config_path):
    filtered = {}
    # Normalize the config path (handle symlinks like /tmp -> /private/tmp on macOS)
    config_path = os.path.realpath(config_path)
    for tool_name, versions in tools.items():
        filtered_versions = []
        for version_info in versions:
            source = version_info.get("source", {})
            source_path = source.get("path", "")
            # Normalize source path and compare
            if source_path and os.path.realpath(source_path) == config_path:
                filtered_versions.append(version_info)
        if filtered_versions:
            filtered[tool_name] = filtered_versions
    return filtered


def get_installed_tools(tools):
    installed = []
    for tool_name, versions in tools.items():
        for version_info in versions:
            if version_info.get("installed", False):
                tool_spec = f"{tool_name}@{version_info.get('version')}"
                installed.append(tool_spec)
    return installed


def get_missing_tools(tools):
    missing = []
    for tool_name, versions in tools.items():
        for version_info in versions:
            if not version_info.get("installed", False):
                tool_spec = f"{tool_name}@{version_info.get('version')}"
                missing.append(tool_spec)
    return missing


def get_config_dir(module):
    path = module.params.get("path")
    if path:
        config_dir = os.path.dirname(os.path.abspath(path))
        if config_dir:
            return config_dir
    return None


def install_tools(module, tools):
    missing = get_missing_tools(tools)

    if not missing:
        return False, [], get_installed_tools(tools)

    cwd = get_config_dir(module)
    result = run_mise_command(module, ["install"] + missing, cwd=cwd)

    return True, missing, get_installed_tools(tools)


def uninstall_tools(module, tools):
    installed = get_installed_tools(tools)

    if not installed:
        return False, installed, []

    cwd = get_config_dir(module)
    result = run_mise_command(module, ["uninstall"] + installed, cwd=cwd)

    return True, installed, []


def run_module():
    module_args = dict(
        path=dict(type="path", required=False, default=None),
        **{"global": dict(type="bool", required=False, default=False)},
        trust=dict(type="bool", required=False, default=False),
        state=dict(
            type="str", required=False, default="present", choices=["present", "absent"]
        ),
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True,
    )

    trust_config(module)

    tools = get_tools_state(module)

    if module.params["state"] == "present":
        changed, missing, installed = install_tools(module, tools)
        module.exit_json(
            changed=changed,
            missing_tools=missing,
            installed_tools=installed,
        )
    else:
        changed, uninstalled, installed = uninstall_tools(module, tools)
        module.exit_json(
            changed=changed,
            installed_tools=installed,
            missing_tools=uninstalled,
        )


def main():
    run_module()


if __name__ == "__main__":
    main()
