# dfa_101_simulator.py

def dfa_accepts_101(input_string):
    current_state = 'q0'
    for char in input_string:
        if current_state == 'q0':
            if char == '0':
                current_state = 'q0'
            elif char == '1':
                current_state = 'q1'
            else: # Should not happen with binary strings
                return False 
        elif current_state == 'q1':
            if char == '0':
                current_state = 'q2'
            elif char == '1':
                current_state = 'q1'
            else:
                return False
        elif current_state == 'q2':
            if char == '0':
                current_state = 'q0'
            elif char == '1':
                current_state = 'q3'
            else:
                return False
        elif current_state == 'q3':
            pass # Stays in accept state
        # No need for an else here if states are q0, q1, q2, q3
            
    return current_state == 'q3'

if __name__ == "__main__":
    test_inputs = {
        "101": True,
        "001010": True,
        "1110101": True,
        "1001": False,
        "000": False,
        "1": False,
        "10": False,
        "": False,
        "010010": False,
        "1010101": True
    }

    print("--- DFA for '101' Substring Test ---")
    all_passed = True
    for s, expected_result in test_inputs.items():
        if not all(c in '01' for c in s): # Basic validation for binary string
            print(f"Input '{s}': Invalid characters. Skipping.")
            continue
        
        actual_result = dfa_accepts_101(s)
        status = "PASS" if actual_result == expected_result else "FAIL"
        if actual_result != expected_result:
            all_passed = False
        
        print(f"Input: '{s}', Expected: {'Accepted' if expected_result else 'Rejected'}, Got: {'Accepted' if actual_result else 'Rejected'} - {status}")

    if all_passed:
        print("\nAll predefined tests passed!")
    else:
        print("\nSome predefined tests failed.")
    print("--------------------------------------")