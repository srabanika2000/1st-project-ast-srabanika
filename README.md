python --version
git clone https://github.com/your-username/rule-based-evaluation.git
cd rule-based-evaluation
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
POST /create_rule
{
    "rule": "age > 30"
}
{
    "message": "Rule created successfully"
}
POST /combine_rules
{
    "rule_ids": [1, 2]
}
{
    "data": {
        "age": 35,
        "salary": 50000
    },
    "rule": "age > 30 AND salary > 40000"
}
{
    "result": true
}
rule-based-evaluation/
│
├── app.py            # Main application file
├── rules.db          # SQLite database file
├── requirements.txt  # Python dependencies
└── README.md         # Project documentation
