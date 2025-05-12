# test_gnf_converter.py
import unittest
from gnf_converter import (
    parse_grammar,
    find_nullable_non_terminals,
    eliminate_epsilon_productions,
    eliminate_unit_productions,
    eliminate_direct_left_recursion,
    substitute_to_start_terminals,
    finalize_gnf_rhs
)

class TestGNFConverter(unittest.TestCase):

    def test_parse_simple(self):
        cfg_text = "S -> a S | b"
        grammar, nt, t, start, _ = parse_grammar(cfg_text)
        expected_grammar = {'S': [['a', 'S'], ['b']]}
        self.assertEqual(grammar, expected_grammar)
        self.assertEqual(nt, ['S'])
        self.assertEqual(t, ['a', 'b'])
        self.assertEqual(start, 'S')

    def test_parse_epsilon(self):
        cfg_text = "S -> a | epsilon"
        grammar, _, _, _, _ = parse_grammar(cfg_text)
        expected_grammar = {'S': [['a'], ['!epsilon']]}
        self.assertEqual(grammar, expected_grammar)

    def test_parse_multiple_rules(self):
        cfg_text = """
        S -> A B | C
        A -> a
        B -> b
        C -> c C | epsilon
        """
        grammar, nt, t, start, _ = parse_grammar(cfg_text)
        self.assertEqual(start, 'S')
        self.assertCountEqual(nt, ['S', 'A', 'B', 'C'])
        self.assertCountEqual(t, ['a', 'b', 'c'])
        self.assertEqual(grammar['S'], [['A', 'B'], ['C']])
        self.assertEqual(grammar['C'], [['c', 'C'], ['!epsilon']])

    def test_parse_invalid_rule(self):
        cfg_text = "S -> a S b -> c"
        expected_grammar = {'S': [['a', 'S', 'b', '->', 'c']]}
        grammar, _, _, _, _ = parse_grammar(cfg_text)
        self.assertEqual(grammar, expected_grammar)


    def test_parse_empty(self):
        cfg_text = ""
        grammar, _, _, _, _ = parse_grammar(cfg_text)
        self.assertIsNone(grammar)

    def test_nullable_simple(self):
        grammar = {'S': [['A'], ['a']], 'A': [['!epsilon']]}
        nt = ['S', 'A']
        nullable = find_nullable_non_terminals(grammar, nt)
        self.assertEqual(nullable, {'A', 'S'})

    def test_nullable_indirect(self):
        grammar = {'S': [['A', 'B']], 'A': [['C']], 'B': [['!epsilon']], 'C': [['!epsilon']]}
        nt = ['S', 'A', 'B', 'C']
        nullable = find_nullable_non_terminals(grammar, nt)
        self.assertEqual(nullable, {'A', 'B', 'C', 'S'})

    def test_nullable_none(self):
         grammar = {'S': [['a', 'S'], ['b']]}
         nt = ['S']
         nullable = find_nullable_non_terminals(grammar, nt)
         self.assertEqual(nullable, set())

    def test_eliminate_epsilon_basic(self):
        grammar = {'S': [['A'], ['a']], 'A': [['!epsilon']]}
        nt = ['S', 'A']; start = 'S'; orig_nt = set(nt)
        g_no_eps, nt_no_eps = eliminate_epsilon_productions(grammar, nt, start, orig_nt)
        expected_g = {'S': sorted([['!epsilon'], ['a']], key=str)}
        expected_nt = ['S']
        self.assertEqual(g_no_eps, expected_g)
        self.assertEqual(nt_no_eps, expected_nt)

    def test_eliminate_epsilon_start_nullable(self):
        grammar = {'S': [['A'], ['!epsilon']], 'A': [['a']]}
        nt = ['S', 'A']; start = 'S'; orig_nt = set(nt)
        g_no_eps, nt_no_eps = eliminate_epsilon_productions(grammar, nt, start, orig_nt)
        expected_g = {'S': sorted([['!epsilon'], ['A']], key=str), 'A': [['a']]}
        for k_actual in g_no_eps: g_no_eps[k_actual].sort(key=str)
        for k_expected in expected_g: expected_g[k_expected].sort(key=str)
        self.assertEqual(g_no_eps, expected_g)
        self.assertCountEqual(nt_no_eps, ['A', 'S'])

    def test_eliminate_epsilon_cascade(self):
         grammar = {'S': [['A', 'B']], 'A': [['!epsilon']], 'B': [['!epsilon']]}
         nt = ['S', 'A', 'B']; start = 'S'; orig_nt = set(nt)
         g_no_eps, nt_no_eps = eliminate_epsilon_productions(grammar, nt, start, orig_nt)
         expected_g = {'S': [['!epsilon']]}
         expected_nt = ['S']
         self.assertEqual(g_no_eps, expected_g)
         self.assertEqual(nt_no_eps, expected_nt)

    def test_eliminate_unit_basic(self):
        grammar = {'S': [['A'], ['a']], 'A': [['B']], 'B': [['b']]}
        nt = ['S', 'A', 'B']
        g_no_unit, nt_no_unit = eliminate_unit_productions(grammar, nt)
        expected_g = {'S': sorted([['a'], ['b']]), 'A': [['b']], 'B': [['b']]}
        for k_actual in g_no_unit: g_no_unit[k_actual].sort(key=str)
        for k_expected in expected_g: expected_g[k_expected].sort(key=str)
        self.assertEqual(g_no_unit, expected_g)
        self.assertCountEqual(nt_no_unit, ['A', 'B', 'S'])

    def test_eliminate_unit_cycle(self):
        grammar = {'S': [['A'], ['c']], 'A': [['B']], 'B': [['S'], ['b']]}
        nt = ['S', 'A', 'B']
        g_no_unit, nt_no_unit = eliminate_unit_productions(grammar, nt)
        expected_g = {'S': sorted([['b'], ['c']]), 'A': sorted([['b'], ['c']]), 'B': sorted([['b'], ['c']])}
        for k_actual in g_no_unit: g_no_unit[k_actual].sort(key=str)
        for k_expected in expected_g: expected_g[k_expected].sort(key=str)
        self.assertEqual(g_no_unit, expected_g)
        self.assertCountEqual(nt_no_unit, ['A', 'B', 'S'])

    def test_eliminate_left_recursion_simple(self):
        grammar = {'E': [['E', '+', 'T'], ['T']], 'T':[]}
        nt_all = {'E', 'T'}
        new_nt = eliminate_direct_left_recursion(grammar, 'E', nt_all)
        self.assertEqual(new_nt, "E'")
        self.assertCountEqual(grammar['E'], [['T'], ['T', "E'"]])
        self.assertCountEqual(grammar["E'"], [['+', 'T'], ['+', 'T', "E'"]])

    def test_finalize_rhs_simple(self):
        grammar = {'A': [['b', 'S', 'B', 'a']], 'S':[], 'B':[]}
        nt = ['A', 'S', 'B']
        orig_nt = set(nt)
        final_g, final_nt_list = finalize_gnf_rhs(grammar, nt, orig_nt)
        self.assertIn('X_A', final_g)
        self.assertEqual(final_g['X_A'], [['a']])
        self.assertEqual(final_g['A'], [['b', 'S', 'B', 'X_A']])
        self.assertCountEqual(final_nt_list, ['A', 'X_A'])

    def test_full_conversion_example1(self):
         cfg_text = """
         S -> A B | a
         A -> b S | c
         B -> S a | epsilon
         """
         g, nt, t, start, orig_nt = parse_grammar(cfg_text)
         self.assertIsNotNone(g)
         g1, nt1 = eliminate_epsilon_productions(g, nt, start, orig_nt)
         self.assertTrue(g1)
         g2, nt2 = eliminate_unit_productions(g1, nt1)
         self.assertTrue(g2)
         g3 = {k: [p[:] for p in v] for k, v in g2.items()}
         nt3 = list(nt2)
         new_nts3 = set()
         for n_loop in list(nt3):
             if n_loop in g3:
                  nn = eliminate_direct_left_recursion(g3, n_loop, set(nt3)|new_nts3)
                  if nn: new_nts3.add(nn)
         nt3_final_list = sorted(list(set(nt3)|new_nts3))
         nt3_final = [n for n in nt3_final_list if n in g3 and g3[n]]
         g3_final = {n:g3[n] for n in nt3_final}

         g4 = {k: [p[:] for p in v] for k, v in g3_final.items()} if g3_final else {}
         nt4 = list(nt3_final) if g3_final else []
         if g4 : substitute_to_start_terminals(g4, nt4)
         nt4_final = sorted([n for n in nt4 if n in g4 and g4[n]])
         g4_final = {n:g4[n] for n in nt4_final}

         g5_final, nt5_final = finalize_gnf_rhs(g4_final, nt4_final, orig_nt) if g4_final else ({}, [])
         self.assertTrue(g5_final)

         for V_test, prods_test in g5_final.items():
             for p_test in prods_test:
                 self.assertTrue(p_test)
                 if p_test == ['!epsilon']:
                     self.assertEqual(V_test, start)
                     continue
                 self.assertIn(p_test[0], t)
                 for symbol_idx, symbol_test in enumerate(p_test[1:]):
                      self.assertIn(symbol_test, nt5_final)

if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)