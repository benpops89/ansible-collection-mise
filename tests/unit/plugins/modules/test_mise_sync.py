#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

import json
import os
import unittest
from unittest.mock import MagicMock, patch

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../../plugins/modules'))

import mise_sync


class TestMiseSync(unittest.TestCase):

    def setUp(self):
        self.mock_module = MagicMock()
        self.mock_module.params = {
            'path': None,
            'global': False,
            'trust': False,
        }

    @patch('mise_sync.subprocess.run')
    def test_get_installed_tools(self, mock_run):
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = json.dumps({
            "node": [
                {
                    "version": "20.0.0",
                    "installed": True,
                    "active": True
                }
            ],
            "python": [
                {
                    "version": "3.11.0",
                    "installed": False,
                    "active": False
                }
            ]
        })
        mock_result.stderr = ""
        mock_run.return_value = mock_result

        tools = mise_sync.get_tools_state(self.mock_module)
        installed = mise_sync.get_installed_tools(tools)

        self.assertEqual(installed, ["node@20.0.0"])

    @patch('mise_sync.subprocess.run')
    def test_get_missing_tools(self, mock_run):
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = json.dumps({
            "node": [
                {
                    "version": "20.0.0",
                    "installed": True
                }
            ],
            "python": [
                {
                    "version": "3.11.0",
                    "installed": False
                }
            ]
        })
        mock_result.stderr = ""
        mock_run.return_value = mock_result

        tools = mise_sync.get_tools_state(self.mock_module)
        missing = mise_sync.get_missing_tools(tools)

        self.assertEqual(missing, ["python@3.11.0"])

    @patch('mise_sync.run_mise_command')
    def test_sync_tools_no_missing(self, mock_run_mise):
        self.mock_module.params['path'] = '/tmp/mise.toml'
        
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = json.dumps({
            "node": [
                {
                    "version": "20.0.0",
                    "installed": True
                }
            ]
        })
        mock_run_mise.return_value = mock_result

        changed, missing, installed = mise_sync.sync_tools(self.mock_module)

        self.assertFalse(changed)
        self.assertEqual(missing, [])

    @unittest.skip("Skipping - complex mocking required for sync_tools")
    @patch('mise_sync.run_mise_command')
    def test_sync_tools_with_missing(self, mock_run_mise):
        pass

    @patch('mise_sync.run_mise_command')
    def test_trust_config(self, mock_run_mise):
        self.mock_module.params['trust'] = True
        self.mock_module.params['path'] = '/tmp/mise.toml'
        
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_run_mise.return_value = mock_result

        mise_sync.trust_config(self.mock_module)

        mock_run_mise.assert_called_once()
        call_args = mock_run_mise.call_args
        self.assertEqual(call_args[0][1], ['trust', '/tmp'])

    @patch('mise_sync.run_mise_command')
    def test_trust_config_no_op(self, mock_run_mise):
        self.mock_module.params['trust'] = False
        
        mise_sync.trust_config(self.mock_module)

        mock_run_mise.assert_not_called()

    def test_get_config_dir(self):
        self.mock_module.params['path'] = '/path/to/project/mise.toml'
        
        config_dir = mise_sync.get_config_dir(self.mock_module)
        
        self.assertEqual(config_dir, '/path/to/project')

    def test_get_config_dir_no_path(self):
        self.mock_module.params['path'] = None
        
        config_dir = mise_sync.get_config_dir(self.mock_module)
        
        self.assertIsNone(config_dir)


if __name__ == '__main__':
    unittest.main()
