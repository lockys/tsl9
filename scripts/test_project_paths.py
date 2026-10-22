"""Offline resolver tests using synthetic paths and environment data only."""
import importlib.util
import os
from pathlib import Path
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('project_paths',Path(__file__).with_name('project_paths.py'))
paths = importlib.util.module_from_spec(spec)
spec.loader.exec_module(paths)


class Paths(unittest.TestCase):
    def test_root_follows_script_not_cwd(self):
        self.assertEqual(paths.project_root(),Path(__file__).resolve().parents[1])

    def test_explicit_llvm_with_spaces(self):
        tool_dir = Path('synthetic tools/LLVM bin').resolve()
        with patch.dict(os.environ,{'TSL9_LLVM_BIN':str(tool_dir)},clear=True), patch.object(Path,'is_file',return_value=True):
            self.assertEqual(paths.llvm_bin(),tool_dir)

    def test_invalid_explicit_llvm_does_not_fall_back(self):
        with patch.dict(os.environ,{'TSL9_LLVM_BIN':'missing'},clear=True), patch.object(Path,'is_file',return_value=False), patch.object(paths.shutil,'which') as which:
            with self.assertRaisesRegex(ValueError,'TSL9_LLVM_BIN'):
                paths.llvm_bin()
            which.assert_not_called()

    def test_ndk_home_finds_one_complete_host_toolchain(self):
        base = Path('synthetic NDK/toolchains/llvm/prebuilt/host/bin').resolve()
        with patch.dict(os.environ,{'ANDROID_NDK_HOME':'synthetic NDK'},clear=True), patch.object(Path,'glob',return_value=[base]), patch.object(Path,'is_file',return_value=True):
            self.assertEqual(paths.llvm_bin(),base)

    def test_multiple_ndk_hosts_are_not_guessed(self):
        hosts = [Path('NDK/host one/bin'),Path('NDK/host two/bin')]
        with patch.dict(os.environ,{'ANDROID_NDK_ROOT':'NDK'},clear=True), patch.object(Path,'glob',return_value=hosts), patch.object(Path,'is_file',return_value=True):
            with self.assertRaisesRegex(ValueError,'TSL9_LLVM_BIN'):
                paths.llvm_bin()

    def test_missing_llvm_is_actionable(self):
        with patch.dict(os.environ,{},clear=True), patch.object(paths.shutil,'which',return_value=None):
            with self.assertRaisesRegex(ValueError,'TSL9_LLVM_BIN'):
                paths.llvm_bin()

    def test_path_requires_all_three_tools(self):
        base = Path('synthetic clang').resolve()
        with patch.dict(os.environ,{},clear=True), patch.object(paths.shutil,'which',return_value=str(base/'clang')), patch.object(Path,'is_file',side_effect=lambda p=False: False):
            with self.assertRaises(ValueError):
                paths.llvm_bin()

    def test_radare2_explicit(self):
        exe = Path('synthetic tools/r2').resolve()
        with patch.dict(os.environ,{'TSL9_R2':str(exe)},clear=True), patch.object(Path,'is_file',return_value=True):
            self.assertEqual(paths.radare2(),exe)

    def test_workspace_is_required_not_guessed(self):
        with patch.dict(os.environ,{},clear=True):
            with self.assertRaisesRegex(ValueError,'TSL9_ANALYSIS_WORKSPACE'):
                paths.analysis_workspace()


if __name__=='__main__':
    unittest.main()
