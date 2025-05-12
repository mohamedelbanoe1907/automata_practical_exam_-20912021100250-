# gnf_converter.py
import itertools
import re

def parse_grammar(input_text):
    grammar = {}
    discovered_non_terminals_lhs = set()
    all_symbols_in_rhs = set()
    first_lhs = None
    original_non_terminals = set()

    lines = [line.strip() for line in input_text.strip().split('\n') if line.strip()]

    if not lines:
        print("Error: Input is empty or contains no rules.")
        return None, [], [], None, set()

    for line in lines:
        if '->' not in line:
            print(f"Error: Line '{line}' does not contain '->'.")
            return None, [], [], None, set()
        lhs, _ = line.split('->', 1)
        lhs = lhs.strip()
        if first_lhs is None and lhs: first_lhs = lhs
        if not lhs:
            print(f"Error: Empty non-terminal on LHS in line '{line}'.")
            return None, [], [], None, set()
        discovered_non_terminals_lhs.add(lhs)
        original_non_terminals.add(lhs)
        if lhs not in grammar: grammar[lhs] = []

    for line in lines:
        lhs, rhs_str = line.split('->', 1)
        lhs = lhs.strip()
        productions_alternatives = rhs_str.split('|')
        current_productions_for_lhs = []
        for alt in productions_alternatives:
            alt_stripped = alt.strip()
            if alt_stripped.lower() in ["epsilon", "eps", "ε"]:
                symbols_in_production = ["!epsilon"]
            else:
                symbols_in_production = alt_stripped.split()
            if not symbols_in_production and alt_stripped.lower() not in ["epsilon", "eps", "ε"]:
                continue
            current_productions_for_lhs.append(symbols_in_production)
            for sym in symbols_in_production:
                if sym != "!epsilon": all_symbols_in_rhs.add(sym)
        if current_productions_for_lhs and lhs in grammar:
            grammar[lhs].extend(current_productions_for_lhs)

    final_non_terminals_set = set(nt for nt in discovered_non_terminals_lhs if nt in grammar and grammar[nt])
    active_grammar = {nt: grammar[nt] for nt in final_non_terminals_set}
    final_non_terminals = sorted(list(final_non_terminals_set))

    terminals = set()
    all_symbols_in_active_rhs = set(sym for nt in active_grammar for prod in active_grammar[nt] for sym in prod if sym != '!epsilon')
    for sym in all_symbols_in_active_rhs:
         if sym not in original_non_terminals:
              terminals.add(sym)

    if not active_grammar and lines:
        print("Error: No valid rules were parsed.")
        return None, [], [], None, set()

    return active_grammar, final_non_terminals, sorted(list(terminals)), first_lhs, original_non_terminals

def find_nullable_non_terminals(grammar, non_terminals):
    nullable = set()
    non_terminals_set = set(non_terminals)
    for V in non_terminals:
        if V in grammar:
            if any(prod == ['!epsilon'] for prod in grammar[V]): nullable.add(V)
    changed = True
    while changed:
        changed = False
        for V in non_terminals:
            if V in nullable: continue
            if V not in grammar: continue
            for production in grammar[V]:
                if production == ['!epsilon']: continue
                if production:
                    all_syms_nullable = True
                    for symbol in production:
                        is_terminal = symbol not in non_terminals_set
                        if not is_terminal and symbol not in nullable:
                            all_syms_nullable = False; break
                        elif is_terminal and symbol != '!epsilon':
                             all_syms_nullable = False; break
                    if all_syms_nullable:
                        if V not in nullable: nullable.add(V); changed = True
                        break
    return nullable

def eliminate_epsilon_productions(grammar, non_terminals, start_symbol, original_non_terminals_set):
    nullable_set = find_nullable_non_terminals(grammar, non_terminals)
    start_symbol_was_nullable = start_symbol in nullable_set
    new_grammar = {}

    for V in non_terminals:
        if V not in grammar: continue
        new_productions_for_V_set = set()
        for production in grammar[V]:
            nullable_indices = [i for i, symbol in enumerate(production) if symbol in nullable_set]
            num_nullable = len(nullable_indices)
            for i in range(1 << num_nullable):
                indices_to_remove = set(nullable_indices[j] for j in range(num_nullable) if (i >> j) & 1)
                new_prod_list = [symbol for idx, symbol in enumerate(production) if idx not in indices_to_remove]
                if new_prod_list:
                    new_productions_for_V_set.add(tuple(new_prod_list))
        
        filtered_prods = {prod for prod in new_productions_for_V_set if prod != ('!epsilon',)}
        if filtered_prods:
             new_grammar[V] = sorted([list(p) for p in filtered_prods], key=str)

    if start_symbol_was_nullable:
        if start_symbol not in new_grammar: new_grammar[start_symbol] = []
        if ['!epsilon'] not in new_grammar[start_symbol]:
            new_grammar[start_symbol].append(['!epsilon'])
            new_grammar[start_symbol].sort(key=str)

    current_grammar = new_grammar
    current_non_terminals = sorted([nt for nt in non_terminals if nt in current_grammar and current_grammar[nt]])

    while True:
        active_nts_in_pass = set(current_non_terminals)
        grammar_after_cleanup = {}
        changed_in_pass = False

        for nt, prods in current_grammar.items():
            valid_prods_for_nt = []
            for prod in prods:
                is_valid_prod = True
                if prod == ['!epsilon']: is_valid_prod = True
                else:
                    for symbol in prod:
                        is_potential_terminal = symbol not in original_non_terminals_set
                        is_active_non_terminal = symbol in active_nts_in_pass
                        if not is_potential_terminal and not is_active_non_terminal:
                            is_valid_prod = False; break
                if is_valid_prod: valid_prods_for_nt.append(prod)

            if valid_prods_for_nt:
                original_prods_before_cleanup = current_grammar.get(nt, [])
                if len(valid_prods_for_nt) < len(original_prods_before_cleanup):
                    changed_in_pass = True
                grammar_after_cleanup[nt] = sorted(valid_prods_for_nt, key=str)
            elif nt in current_grammar:
                 changed_in_pass = True

        current_grammar = grammar_after_cleanup
        current_non_terminals = sorted(current_grammar.keys())
        if not changed_in_pass: break

    return current_grammar, current_non_terminals

def eliminate_unit_productions(grammar, non_terminals):
    if not grammar: return {}, []
    grammar_copy = {k: [p[:] for p in v] for k, v in grammar.items()}
    non_terminals_set = set(non_terminals)

    unit_pairs = set((V, V) for V in non_terminals)
    changed = True
    while changed:
        changed = False
        new_pairs_this_iter = set()
        for A in non_terminals:
            if A not in grammar_copy: continue
            for production in grammar_copy[A]:
                if len(production) == 1 and production[0] in non_terminals_set:
                    B = production[0]
                    if (A, B) not in unit_pairs: new_pairs_this_iter.add((A, B)); changed = True
        unit_pairs.update(new_pairs_this_iter)
        
        new_pairs_transitive = set()
        for A, B in list(unit_pairs):
            for B_prime, C in list(unit_pairs):
                if B == B_prime and (A, C) not in unit_pairs:
                    new_pairs_transitive.add((A, C)); changed = True
        unit_pairs.update(new_pairs_transitive)

    new_grammar = {}
    processed_productions = set()
    for A, B in unit_pairs:
        if B not in grammar_copy: continue
        for production in grammar_copy[B]:
            is_unit = len(production) == 1 and production[0] in non_terminals_set
            if not is_unit:
                prod_tuple = tuple(production)
                prod_key = (A, prod_tuple)
                if prod_key not in processed_productions:
                    if A not in new_grammar: new_grammar[A] = []
                    if production not in new_grammar.get(A, []): new_grammar[A].append(production)
                    processed_productions.add(prod_key)

    for V in new_grammar: new_grammar[V] = sorted(new_grammar[V], key=str)
    final_non_terminals = sorted([nt for nt in non_terminals if nt in new_grammar and new_grammar[nt]])
    final_grammar = {nt: new_grammar[nt] for nt in final_non_terminals}
    return final_grammar, final_non_terminals

def eliminate_direct_left_recursion(grammar, non_terminal, all_non_terminals):
    if non_terminal not in grammar: return None
    
    productions = grammar[non_terminal]
    left_recursive_rules_alpha = []
    non_left_recursive_rules_beta = []

    for prod in productions:
        if prod and prod[0] == non_terminal:
            alpha = prod[1:]
            if not alpha: continue 
            left_recursive_rules_alpha.append(alpha)
        else:
            non_left_recursive_rules_beta.append(prod)

    if not left_recursive_rules_alpha: return None
    if not non_left_recursive_rules_beta:
        if non_terminal in grammar: del grammar[non_terminal]
        return None

    new_nt_name = non_terminal + "'"
    while new_nt_name in all_non_terminals or new_nt_name in grammar: new_nt_name += "'"

    new_A_productions = []
    new_A_prime_productions = []
    for beta in non_left_recursive_rules_beta:
        new_A_productions.append(beta)
        if beta != ['!epsilon']: new_A_productions.append(beta + [new_nt_name])
        else: new_A_productions.append([new_nt_name])
    for alpha in left_recursive_rules_alpha:
        new_A_prime_productions.append(alpha)
        new_A_prime_productions.append(alpha + [new_nt_name])

    grammar[non_terminal] = sorted(new_A_productions, key=str)
    grammar[new_nt_name] = sorted(new_A_prime_productions, key=str)
    return new_nt_name

def substitute_to_start_terminals(grammar, non_terminals):
    if not grammar: return
    non_terminals_set = set(non_terminals)

    made_change_global = True
    iteration_count = 0
    max_iterations = len(non_terminals) * len(non_terminals) + len(non_terminals) + 5 

    while made_change_global and iteration_count < max_iterations:
        made_change_global = False
        iteration_count += 1
        
        keys_to_process = list(grammar.keys())

        for A in keys_to_process:
            if A not in grammar: continue
            
            current_productions_for_A = grammar[A]
            next_productions_for_A = []
            modified_this_A = False

            for production in current_productions_for_A:
                if not production or production == ['!epsilon']:
                    next_productions_for_A.append(production)
                    continue
                
                first_symbol = production[0]
                
                if first_symbol in non_terminals_set and first_symbol in grammar:
                    B = first_symbol
                    gamma = production[1:]
                    modified_this_A = True
                    made_change_global = True

                    for b_production in grammar[B]:
                        if b_production and b_production[0] == A and not gamma:
                            next_productions_for_A.append(production) 
                            continue
                        new_prod = b_production + gamma
                        next_productions_for_A.append(new_prod)
                else:
                    next_productions_for_A.append(production)
            
            if modified_this_A:
                unique_prods = {tuple(p) for p in next_productions_for_A if p}
                final_prods = []
                has_epsilon = False
                for p_tuple in unique_prods:
                    p_list = list(p_tuple)
                    if p_list == ['!epsilon']: has_epsilon = True
                    else: final_prods.append(p_list)
                if has_epsilon: final_prods.append(['!epsilon'])
                
                if final_prods:
                    grammar[A] = sorted(final_prods, key=str)
                elif A in grammar: # Became empty
                     del grammar[A]


    if iteration_count >= max_iterations:
         print(f"Warning: Substitution loop reached max iterations ({max_iterations}).")

def finalize_gnf_rhs(grammar, non_terminals, original_non_terminals_set):
    if not grammar: return {}, []

    final_grammar = {}
    new_nt_map = {} 
    all_new_nt_names_generated = set()
    current_non_terminals_set = set(non_terminals) 

    grammar_keys = list(grammar.keys()) 

    for V in grammar_keys:
        if V not in grammar: continue
        final_prods_for_V = []
        for production in grammar[V]:
            if not production: continue
            if production == ['!epsilon']: 
                final_prods_for_V.append(production); continue

            first_symbol = production[0]
            is_terminal_start = first_symbol not in original_non_terminals_set and first_symbol != '!epsilon'
            if not is_terminal_start:
                # print(f"Error: Rule '{V} -> {' '.join(production)}' doesn't start with terminal before final step!")
                final_prods_for_V.append(production)
                continue

            alpha_part = production[1:]
            new_alpha_part = []
            for symbol in alpha_part:
                is_terminal = symbol not in original_non_terminals_set and symbol != '!epsilon'
                if is_terminal:
                    if symbol not in new_nt_map: 
                        clean_symbol_name = re.sub(r'\W|^(?=\d)', '_', symbol) 
                        base_name = "X_" + clean_symbol_name.upper()
                        new_nt_name = base_name
                        suffix = 1
                        while new_nt_name in original_non_terminals_set or \
                              new_nt_name in current_non_terminals_set or \
                              new_nt_name in all_new_nt_names_generated:
                            new_nt_name = base_name + str(suffix)
                            suffix += 1
                        new_nt_map[symbol] = new_nt_name
                        all_new_nt_names_generated.add(new_nt_name)
                    new_alpha_part.append(new_nt_map[symbol])
                else: 
                    new_alpha_part.append(symbol)

            final_production = [first_symbol] + new_alpha_part
            final_prods_for_V.append(final_production)

        if final_prods_for_V:
            unique_prods = {tuple(p) for p in final_prods_for_V}
            final_grammar[V] = sorted([list(p) for p in unique_prods], key=str)

    for terminal, new_nt_name in new_nt_map.items():
        if new_nt_name not in final_grammar:
             final_grammar[new_nt_name] = []
        if [terminal] not in final_grammar[new_nt_name]:
             final_grammar[new_nt_name].append([terminal])
             final_grammar[new_nt_name].sort(key=str)
    
    combined_non_terminals = set(non_terminals) | all_new_nt_names_generated
    final_active_non_terminals = sorted([nt for nt in combined_non_terminals if nt in final_grammar and final_grammar[nt]])
    truly_final_grammar = {nt: final_grammar[nt] for nt in final_active_non_terminals}

    return truly_final_grammar, final_active_non_terminals

if __name__ == "__main__":

    sample_cfg_text_1 = """
    S -> A B | a
    A -> b S | c
    B -> S a | epsilon
    """
    sample_cfg_text_2 = """
    E -> E + T | T
    T -> T * F | F
    F -> ( E ) | id
    """
    sample_cfg_text_3 = """
    S -> A a A | B b B | epsilon
    A -> epsilon
    B -> epsilon
    C -> A B
    D -> C c
    E -> D
    F -> f
    """
    sample_cfg_text_4_units = """
    S -> A | B | c
    A -> B | a
    B -> S | b
    """

    tests = {
        "Example 1": sample_cfg_text_1,
        "Example 2 (Expr)": sample_cfg_text_2,
        "Example 3 (Seq Nullable)": sample_cfg_text_3,
        "Example 4 (Unit Cycles)": sample_cfg_text_4_units
    }

    def print_grammar(grammar_dict, title="Grammar"):
        print(f"=== {title} ===")
        if not grammar_dict: print("  (Grammar is empty)"); return
        for V in sorted(grammar_dict.keys()):
            prods = grammar_dict.get(V, [])
            prods_str_list = []
            sorted_prods = sorted(prods, key=lambda p: (p == ['!epsilon'], str(p)))
            for p in sorted_prods:
                prods_str_list.append("eps" if p == ['!epsilon'] else " ".join(p)) # Changed to 'eps'
            if prods_str_list: print(f"  {V} -> " + " | ".join(prods_str_list))

    for test_name, cfg_text in tests.items():
        print(f"\n--- Testing {test_name} ---")
        parsed_grammar, parsed_non_terminals, parsed_terminals, detected_start_symbol, original_non_terminals = parse_grammar(cfg_text)

        if parsed_grammar:
            start_symbol = detected_start_symbol
            if not start_symbol:
                 if parsed_non_terminals: start_symbol = parsed_non_terminals[0]
                 else: print("Error: Cannot determine start symbol."); continue

            print_grammar(parsed_grammar, title="Original Grammar")
            print(f"\nStart Symbol: {start_symbol}")
            print(f"Non-Terminals: {parsed_non_terminals}")
            print(f"Terminals: {parsed_terminals}")
            nullable_set = find_nullable_non_terminals(parsed_grammar, parsed_non_terminals)
            print(f"Nullable Set: {nullable_set if nullable_set else 'None'}")

            current_grammar, current_nt = parsed_grammar, parsed_non_terminals

            grammar_step1, nt_step1 = eliminate_epsilon_productions(current_grammar, current_nt, start_symbol, original_non_terminals)
            print_grammar(grammar_step1, title="1. After Epsilon Elimination")
            print(f"Non-Terminals: {nt_step1}")
            current_grammar, current_nt = grammar_step1, nt_step1

            if current_grammar:
                grammar_step2, nt_step2 = eliminate_unit_productions(current_grammar, current_nt)
                print_grammar(grammar_step2, title="2. After Unit Production Elimination")
                print(f"Non-Terminals: {nt_step2}")
                current_grammar, current_nt = grammar_step2, nt_step2
            
            if current_grammar:
                grammar_step3 = {k: [p[:] for p in v] for k, v in current_grammar.items()}
                nt_step3 = list(current_nt)
                newly_added_nts_step3 = set()
                
                for nt_to_process in list(nt_step3):
                    if nt_to_process in grammar_step3:
                        all_current_nts_for_lr = set(nt_step3) | newly_added_nts_step3
                        new_nt_name = eliminate_direct_left_recursion(grammar_step3, nt_to_process, all_current_nts_for_lr)
                        if new_nt_name: newly_added_nts_step3.add(new_nt_name)
                
                final_non_terminals_step3_set = set(nt_step3) | newly_added_nts_step3
                final_non_terminals_step3 = sorted([nt for nt in final_non_terminals_step3_set if nt in grammar_step3 and grammar_step3[nt]])
                final_grammar_step3 = {nt: grammar_step3[nt] for nt in final_non_terminals_step3}
                print_grammar(final_grammar_step3, title="3. After Direct Left Recursion Elimination")
                print(f"Non-Terminals: {final_non_terminals_step3}")
                current_grammar, current_nt = final_grammar_step3, final_non_terminals_step3
            
            if current_grammar:
                grammar_step4 = {k: [p[:] for p in v] for k, v in current_grammar.items()}
                nt_step4 = list(current_nt)
                substitute_to_start_terminals(grammar_step4, nt_step4)
                final_non_terminals_step4 = sorted([nt for nt in nt_step4 if nt in grammar_step4 and grammar_step4[nt]])
                final_grammar_step4 = {nt: grammar_step4[nt] for nt in final_non_terminals_step4}
                print_grammar(final_grammar_step4, title="4. After Substitution to Start Terminals (Simplified)")
                print(f"Non-Terminals: {final_non_terminals_step4}")
                current_grammar, current_nt = final_grammar_step4, final_non_terminals_step4
            
            if current_grammar:
                final_gnf_grammar, final_gnf_non_terminals = finalize_gnf_rhs(current_grammar, current_nt, original_non_terminals)
                print_grammar(final_gnf_grammar, title="5. Final GNF Grammar")
                print(f"Non-Terminals: {final_gnf_non_terminals}")
            
        else:
            print(f"Failed to parse grammar for {test_name}.")
        print("--------------------------------------")