
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/api/ask', methods=['POST'])
def ask():
    x = request.get_json()
    
    return jsonify(x['prompt'])

if __name__ == '__main__':
    app.run(debug=True)