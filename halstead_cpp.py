import re
import sys
from collections import Counter
from math import log2

cpp_operators = [
    '>>=', '<<=', '+=', '-=', '*=', '/=', '%=', '&=', '^=', '|=', '>>', '<<',
    '++', '--', '->*', '->', '&&', '||', '>=', '<=', '==', '!=', ';', '{', '}',
    '[', ']', '(', ')', '.', '->', '&', '*', '+', '-', '~', '!', '/', '%', '<',
    '>', '^', '|', '?', ':', '=', ',', '#', '##', '...', 'new', 'delete'
]

cpp_keywords = [
    'alignas', 'alignof', 'and', 'and_eq', 'asm', 'auto', 'bitand', 'bitor',
    'bool', 'break', 'case', 'catch', 'char', 'class', 'compl', 'const',
    'const_cast', 'continue', 'decltype', 'default', 'delete', 'do', 'double',
    'dynamic_cast', 'else', 'enum', 'explicit', 'export', 'extern', 'false',
    'float', 'for', 'friend', 'goto', 'if', 'inline', 'int', 'long', 'mutable',
    'namespace', 'new', 'noexcept', 'not', 'not_eq', 'nullptr', 'operator', 'or',
    'or_eq', 'private', 'protected', 'public', 'register', 'reinterpret_cast',
    'return', 'short', 'signed', 'sizeof', 'static', 'static_cast', 'struct',
    'switch', 'template', 'this', 'throw', 'true', 'try', 'typedef', 'typeid',
    'typename', 'union', 'unsigned', 'using', 'virtual', 'void', 'volatile',
    'wchar_t', 'while', 'xor', 'xor_eq'
]

operators = set(cpp_operators + cpp_keywords)

def tokenize_code(code):
    # Remove comments and strings
    code = re.sub(r'//.*?$', '', code, flags=re.MULTILINE)
    code = re.sub(r'/\*.*?\*/', '', code, flags=re.DOTALL)
    code = re.sub(r'"(?:\\.|[^"\\])*"', '', code)
    code = re.sub(r"'(?:\\.|[^'\\])*'", '', code)

    # Pattern for operators and identifiers
    operator_pattern = '|'.join(re.escape(op) for op in sorted(operators, key=lambda x: -len(x)))
    pattern = r'(' + operator_pattern + r')|(\b\w+\b)'

    tokens = re.findall(pattern, code)
    tokens = [token[0] if token[0] else token[1] for token in tokens if token]
    return tokens

def count_operators_operands(tokens):
    operator_count = Counter()
    operand_count = Counter()

    for token in tokens:
        if token in operators:
            operator_count[token] += 1
        elif re.match(r'^\w+$', token):
            operand_count[token] += 1

    n1 = len(operator_count)
    n2 = len(operand_count)
    N1 = sum(operator_count.values())
    N2 = sum(operand_count.values())

    return n1, n2, N1, N2, operator_count, operand_count

def calculate_halstead(n1, n2, N1, N2):
    n = n1 + n2
    N = N1 + N2

    if n == 0 or N == 0:
        return None

    estimated_N = (n1 * log2(n1) + n2 * log2(n2)) if n1 > 0 and n2 > 0 else 0
    V = N * log2(n) if n > 0 else 0
    D = (n1 / 2) * (N2 / n2) if n2 > 0 else 0
    E = D * V
    T = E / 18
    B = V / 3000

    return {
        'Vocabulary (n)': n,
        'Length (N)': N,
        'Estimated Length': estimated_N,
        'Volume (V)': V,
        'Difficulty (D)': D,
        'Effort (E)': E,
        'Time (T)': T,
        'Bugs (B)': B
    }

def calculate_cyclomatic_complexity(code):
    decision_keywords = [
        r'\bif\b', r'\belse if\b', r'\bfor\b', r'\bwhile\b', 
        r'\bcase\b', r'\bcatch\b', r'&&', r'\|\|', r'\?'
    ]
    # Escapa caracteres especiales y busca decisiones
    decisions = sum(len(re.findall(keyword, code)) for keyword in decision_keywords)
    return decisions + 1  # Adding 1 for the default path

def count_lines_of_code(code):
    total_lines = code.splitlines()
    code_lines = [line for line in total_lines if line.strip() and not line.strip().startswith('//') and not line.strip().startswith('/*')]
    return len(total_lines), len(code_lines)

def analyze_cpp_code(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        code = f.read()

    # Tokenize and calculate Halstead metrics
    tokens = tokenize_code(code)
    n1, n2, N1, N2, operator_count, operand_count = count_operators_operands(tokens)
    halstead_metrics = calculate_halstead(n1, n2, N1, N2)

    # Calculate Cyclomatic Complexity
    cyclomatic_complexity = calculate_cyclomatic_complexity(code)

    # Count Lines of Code
    total_lines, code_lines = count_lines_of_code(code)

    # Display Results
    print(f"\nHalstead Metrics:\n")
    for key, value in halstead_metrics.items():
        print(f"{key}: {value:.2f}" if isinstance(value, float) else f"{key}: {value}")

    print(f"\nCyclomatic Complexity: {cyclomatic_complexity}")
    print(f"Total Lines: {total_lines}")
    print(f"Code Lines: {code_lines}")

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python analyze_cpp.py <path_to_cpp_file>")
        sys.exit(1)

    file_path = sys.argv[1]
    analyze_cpp_code(file_path)
