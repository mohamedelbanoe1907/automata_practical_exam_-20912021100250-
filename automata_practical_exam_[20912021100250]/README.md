Automata Practical Exam Submission

Name:[محمد عبدالبديع فتحي محمد]
ID:[20912021100250]

---

Project Structure

- `problem1_dfa_101/`: Contains the DFA design for the first problem. - the DFA and its state diagram are provided in the PDF file located at:
  `problem1_dfa_101/DFA_Problem1_Solution.pdf`

- `problem2_cfg_to_gnf/`: Contains the Python program for converting Context-Free Grammars (CFG) to Greibach Normal Form (GNF).

  - `gnf_converter.py`: The main program script.
  - `test_gnf_converter.py`: Unit tests for the GNF converter.

- `problem3_tm_divisible_by_3/`: Contains the Python program for the Turing Machine for the third problem.

  - `tm_divisible_by_3.py`: The main script for the Turing Machine and its simulation.
  - `test_tm_divisible_by_3.py`: Unit tests for the Turing Machine.

- `README.md`: This file (overall project description).

- `requirements.txt`: Dependencies file (indicates no external libraries).

---

Section 1: DFA Design

Task Being Solved: Construct a DFA that accepts all binary strings where the substring "101" appears at least once.
Solution Description and Diagram:
The detailed formal description of the DFA and its state diagram are provided in the PDF file located at:
`problem1_dfa_101/DFA_Problem1_Solution.pdf`

---

Section 2: CFG to GNF Converter

Task Being Solved: Write a program to convert a CFG to GNF.

Code Location: `problem2_cfg_to_gnf/` - `gnf_converter.py` (main program) - `test_gnf_converter.py` (unit tests)
How to run: - To run the main program with built-in examples:
`bash
      cd problem2_cfg_to_gnf
      python gnf_converter.py
      ` - Input format in code: `S -> A B | epsilon`. `epsilon` or `eps` for empty string.
How to test: - To run unit tests:
`bash
      cd problem2_cfg_to_gnf
      python test_gnf_converter.py
      `

---

Section 3: Turing Machine for Divisibility by 3

Task Being Solved: Program a Turing Machine to recognize binary numbers divisible by 3.

Code Location: `problem3_tm_divisible_by_3/` - `tm_divisible_by_3.py` (main TM script) - `test_tm_divisible_by_3.py` (unit tests)
How to run/test: - To run the TM simulation with built-in examples:
`bash
      cd problem3_tm_divisible_by_3
      python tm_divisible_by_3.py
      ` - To run unit tests:
`bash
      cd problem3_tm_divisible_by_3
      python test_tm_divisible_by_3.py
      `
Brief Logic: The TM uses states q_rem0, q_rem1, q_rem2 to track the remainder modulo 3. It accepts if the remainder is 0 at the end of the input. The full transition details are within the `tm_divisible_by_3.py` script.

---
