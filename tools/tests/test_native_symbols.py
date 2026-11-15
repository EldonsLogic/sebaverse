"""Synthetic readelf parsing only; no native file execution or DB access."""
import importlib.util
from pathlib import Path
import unittest

SPEC = importlib.util.spec_from_file_location('native_symbols', Path(__file__).parents[1] / 'security/native_symbols.py')
m = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(m)


class SymbolTests(unittest.TestCase):
    def test_versioned_imports_and_definitions(self):
        text = '''Symbol table '.dynsym' contains 6 entries:
  1: 0000000000000000 0 FUNC GLOBAL DEFAULT UND regcomp@GLIBC_2.2.5 (2)
  2: 0000000000000000 0 FUNC GLOBAL DEFAULT UND __isoc99_fwscanf@GLIBC_2.7 (3)
  3: 0000000000000000 0 FUNC GLOBAL DEFAULT UND dlopen@GLIBC_2.34 (4)
  4: 0000000000012345 22 FUNC GLOBAL DEFAULT 12 regexec@@GLIBC_2.3.4
  5: 0000000000000000 0 FUNC GLOBAL DEFAULT UND scanf@GLIBC_2.2.5 (2)
'''
        result = m.parse_symbols(text)
        self.assertEqual(result['target_imports'], ['__isoc99_fwscanf@GLIBC_2.7', 'regcomp@GLIBC_2.2.5'])
        self.assertEqual(result['target_definitions'], ['regexec@@GLIBC_2.3.4'])
        self.assertEqual(result['dynamic_lookup_imports'], ['dlopen@GLIBC_2.34'])

    def test_wide_aliases(self):
        for name in ['wscanf', 'vfwscanf', '__isoc23_swscanf', '__vfwscanf_internal', '_IO_vfwscanf', '__fwscanf_chk']:
            with self.subTest(name=name):
                self.assertIsNotNone(m.TARGET.fullmatch(name))
        for name in ['scanf', 'sscanf', 'regerror', 'my_regcomp']:
            self.assertIsNone(m.TARGET.fullmatch(name))

    def test_empty_malformed_rejected(self):
        for text in ['', 'readelf error', '1: nonsense']:
            with self.subTest(text=text), self.assertRaisesRegex(ValueError, 'parseable'):
                m.parse_symbols(text)


if __name__ == '__main__':
    unittest.main()
