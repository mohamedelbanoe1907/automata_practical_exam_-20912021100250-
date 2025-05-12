# tm_divisible_by_3.py

class TuringMachine:
    def __init__(self, states, input_alphabet, tape_alphabet, transitions,
                 start_state, accept_state, reject_state, blank_symbol='⊔'):
        self.states = set(states)
        self.input_alphabet = set(input_alphabet)
        self.tape_alphabet = set(tape_alphabet)
        self.transitions = transitions
        self.start_state = start_state
        self.accept_state = accept_state
        self.reject_state = reject_state
        self.blank_symbol = blank_symbol

        for state_from, rules in self.transitions.items():
            if state_from not in self.states:
                raise ValueError(f"State '{state_from}' in transitions is not in defined states.")
            for symbol_read, (state_to, _, _) in rules.items():
                if state_to not in self.states:
                    raise ValueError(f"State '{state_to}' in transition from '{state_from}' "
                                     f"on '{symbol_read}' is not in defined states.")

    def _initialize_tape(self, input_string):
        tape = {}
        for i, char in enumerate(input_string):
            if char not in self.input_alphabet:
                raise ValueError(f"Input symbol '{char}' not in input alphabet.")
            tape[i] = char
        return tape

    def simulate(self, input_string, max_steps=1000):
        if input_string and not all(c in self.input_alphabet for c in input_string):
             # print(f"Error: Input string '{input_string}' contains symbols not in the input alphabet.")
             return False

        tape = self._initialize_tape(input_string)
        current_state = self.start_state
        head_position = 0
        steps = 0

        while steps < max_steps:
            if current_state == self.accept_state:
                return True
            if current_state == self.reject_state:
                return False

            current_symbol_on_tape = tape.get(head_position, self.blank_symbol)

            if current_state not in self.transitions or \
               current_symbol_on_tape not in self.transitions[current_state]:
                return False

            new_state, symbol_to_write, direction = self.transitions[current_state][current_symbol_on_tape]

            tape[head_position] = symbol_to_write
            current_state = new_state

            if direction == 'R':
                head_position += 1
            elif direction == 'L':
                head_position -= 1
            elif direction == 'S':
                pass
            else:
                raise ValueError(f"Invalid direction '{direction}' in transition.")
            steps += 1
        return False


def create_divisible_by_3_tm():
    states = {'q_rem0', 'q_rem1', 'q_rem2', 'q_accept', 'q_reject'}
    input_alphabet = {'0', '1'}
    tape_alphabet = {'0', '1', '⊔'}
    blank_symbol = '⊔'
    start_state = 'q_rem0'
    accept_state = 'q_accept'
    reject_state = 'q_reject'

    transitions = {
        'q_rem0': {
            '0': ('q_rem0', '0', 'R'),
            '1': ('q_rem1', '1', 'R'),
            blank_symbol: ('q_accept', blank_symbol, 'S')
        },
        'q_rem1': {
            '0': ('q_rem2', '0', 'R'),
            '1': ('q_rem0', '1', 'R'),
            blank_symbol: ('q_reject', blank_symbol, 'S')
        },
        'q_rem2': {
            '0': ('q_rem1', '0', 'R'),
            '1': ('q_rem2', '1', 'R'),
            blank_symbol: ('q_reject', blank_symbol, 'S')
        }
    }
    tm = TuringMachine(states, input_alphabet, tape_alphabet, transitions,
                       start_state, accept_state, reject_state, blank_symbol)
    return tm


if __name__ == "__main__":
    tm_div3 = create_divisible_by_3_tm()
    test_strings = [
        "", "0", "1", "10", "11", "100", "101", "110", "111",
        "1000", "1001", "0000", "0011"
    ]
    print("--- Testing Turing Machine for Divisibility by 3 ---")
    for s in test_strings:
        print(f"\nInput: '{s}'")
        result = tm_div3.simulate(s)
        is_divisible_by_3 = False
        if s == "": is_divisible_by_3 = True
        elif s.isdigit():
             try:
                if int(s, 2) % 3 == 0: is_divisible_by_3 = True
             except ValueError: pass
        
        expected_str = "Accept" if is_divisible_by_3 else "Reject"
        actual_str = "Accept" if result else "Reject"
        print(f"Result: {actual_str} (Expected: {expected_str})")
        if actual_str != expected_str:
             print(f"****** MISMATCH for input '{s}' ******")
    print("----------------------------------------------------")