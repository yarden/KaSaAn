#!/usr/bin/env python3

import unittest
from KaSaAn.core import KappaAgent, KappaPort, KappaCounter


class TestKappaAgent(unittest.TestCase):
    """Test various elements of a KappaAgent representation."""
    def test_string_representation(self):
        self.assertEqual(str(KappaAgent('Bob()')), 'Bob()')
        self.assertEqual(str(KappaAgent('Bob(s1)')), 'Bob(s1[#]{#})')
        self.assertEqual(str(KappaAgent('Bob(s2, s1)')), 'Bob(s1[#]{#} s2[#]{#})')
        self.assertEqual(str(KappaAgent('Bob(s1[11]{ph})')), 'Bob(s1[11]{ph})')
        self.assertEqual(str(KappaAgent('Bob(s1{ph}[99])')), 'Bob(s1[99]{ph})')
        self.assertEqual(str(KappaAgent('_1()')), '_1()')
        self.assertEqual(str(KappaAgent('~a()')), '~a()')

    def test_inclusion_criteria(self):
        self.assertTrue('Bob()' in KappaAgent('Bob()'))
        self.assertTrue('s1[.]' in KappaAgent('Bob(s1[.])'))
        self.assertTrue('s1[_]' in KappaAgent('Bob(s1[11])'))
        self.assertFalse('s1[.]' in KappaAgent('Bob(s1[11])'))
        self.assertFalse('s1[_]' in KappaAgent('Bob(s1[.])'))
        self.assertTrue('s2{ph}' in KappaAgent('Bob(s1, s2{ph}[22])'))
        self.assertTrue('s2[11]' in KappaAgent('Bob(s1, s2{ph}[11])'))
        self.assertFalse('s2{ph}' in KappaAgent('Bob(s1, s2{un})'))
        self.assertTrue(KappaAgent('Bob(s1[.]{ph})') in KappaAgent('Bob(s1[.]{ph}, s2[11]{gh})'))
        self.assertTrue('s1[#]' in KappaAgent('Bob(s1[.]{ph}, s2[11]{gh})'))
        self.assertTrue('s1{#}' in KappaAgent('Bob(s1[.]{ph}, s2[11]{gh})'))
        self.assertFalse('s3[#]{#}' in KappaAgent('Bob(s1[.]{ph}, s2[11]{gh})'))

    def test_get_agent_name(self):
        self.assertEqual('Bob', KappaAgent('Bob(s1[_]{pd}, s2[.]{ds})').get_agent_name())
        self.assertEqual('~1', KappaAgent('~1(s1[_]{pd}, s2[.]{ds})').get_agent_name())
        self.assertEqual('_DD', KappaAgent('_DD(s1[_]{pd}, s2[.]{ds})').get_agent_name())

    def test_get_agent_signature(self):
        self.assertEqual('s1[_]{pd}', str(KappaAgent('Bob(s1{pd}[_], s2[.]{ds})').get_agent_signature()[0]))
        self.assertEqual('s2[.]{ds}', str(KappaAgent('Bob(s1{pd}[_], s2[.]{ds})').get_agent_signature()[1]))
        self.assertCountEqual([KappaPort('s1[3]{ph}'), KappaPort('_2'), KappaCounter('c3{=55}')],
                              KappaAgent('Jane(s1{ph}[3], _2, c3{=55})').get_agent_signature())

    def test_get_bond_identifiers(self):
        self.assertCountEqual(['1', '33', '999'], KappaAgent('Mary(~a[1], _b[33], cc[999])').get_bond_identifiers())

    def test_get_abundance_change_operation(self):
        self.assertEqual('+', KappaAgent('Mary(s-1[1]{ph-})+').get_abundance_change_operation())
        self.assertEqual('-', KappaAgent('Mary(s+1[1]{ph+})-').get_abundance_change_operation())
        self.assertEqual('', KappaAgent('Mary(s-1[1]{ph+})').get_abundance_change_operation())
