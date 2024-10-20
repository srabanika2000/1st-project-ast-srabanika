from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)

# Database setup
def init_db():
    conn = sqlite3.connect('rules.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS rules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            rule_text TEXT
        )
    ''')
    conn.commit()
    conn.close()

# Node class for AST
class Node:
    def __init__(self, node_type, value=None, left=None, right=None):
        self.type = node_type
        self.value = value
        self.left = left
        self.right = right

# Function to parse an expression and generate AST
def parse_expression(expression):
    # Break down the expression assuming format like "age > 30"
    tokens = expression.strip().split(" ")
    if len(tokens) == 3:
        return Node("operand", expression)
    return None

# Function to create an AST from a rule string
def create_rule(rule_string):
    try:
        # Replace "AND" and "OR" with actual logical operators
        if ' AND ' in rule_string or ' OR ' in rule_string:
            # Split on the main logical operators
            # Example: "age > 30 AND department = 'Sales'"
            logical_op = 'AND' if ' AND ' in rule_string else 'OR'
            parts = rule_string.split(f' {logical_op} ')
            left = create_rule(parts[0])
            right = create_rule(parts[1])
            return Node("operator", logical_op, left, right)
        else:
            return parse_expression(rule_string)
    except Exception as e:
        return None

# Combine multiple rules into one AST
def combine_rules(rules):
    if len(rules) == 1:
        return create_rule(rules[0])
    
    combined_root = Node("operator", "AND")
    combined_root.left = create_rule(rules[0])
    combined_root.right = combine_rules(rules[1:])
    return combined_root

# Evaluate the rule against data
def evaluate_rule(ast, data):
    if ast is None:
        return False
    
    if ast.type == "operator":
        left = evaluate_rule(ast.left, data)
        right = evaluate_rule(ast.right, data)
        if ast.value == "AND":
            return left and right
        elif ast.value == "OR":
            return left or right
    elif ast.type == "operand":
        try:
            # Parse the operand expression: e.g., "age > 30"
            expression = ast.value
            key, operator, value = expression.split(' ')
            value = int(value) if value.isdigit() else value.strip("'")
            if operator == '>':
                return data.get(key) > value
            elif operator == '<':
                return data.get(key) < value
            elif operator == '=':
                return data.get(key) == value
        except Exception as e:
            return False
    return False

# Flask Routes
@app.route('/create_rule', methods=['POST'])
def api_create_rule():
    rule_string = request.json.get("rule")
    ast = create_rule(rule_string)
    if ast is None:
        return jsonify({"error": "Invalid rule format"}), 400
    
    conn = sqlite3.connect('rules.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO rules (rule_text) VALUES (?)", (rule_string,))
    conn.commit()
    conn.close()
    return jsonify({"message": "Rule created successfully"}), 201

@app.route('/combine_rules', methods=['POST'])
def api_combine_rules():
    rule_ids = request.json.get("rule_ids")
    conn = sqlite3.connect('rules.db')
    cursor = conn.cursor()
    rules = []
    for rule_id in rule_ids:
        cursor.execute("SELECT rule_text FROM rules WHERE id=?", (rule_id,))
        result = cursor.fetchone()
        if result:
            rules.append(result[0])
    conn.close()
    
    combined_ast = combine_rules(rules)
    return jsonify({"message": "Rules combined successfully"})

@app.route('/evaluate_rule', methods=['POST'])
def api_evaluate_rule():
    data = request.json.get("data")
    rule_string = request.json.get("rule")
    ast = create_rule(rule_string)
    if ast is None:
        return jsonify({"error": "Invalid rule format"}), 400
    result = evaluate_rule(ast, data)
    return jsonify({"result": result})

# Initialize the database
init_db()

if __name__ == '__main__':
    app.run(debug=True)
