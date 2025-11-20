from flask import Flask, request, jsonify, render_template
from datetime import datetime
import json

app = Flask(__name__)

# Using in-memory storage (list) for demo. In production use a database.
exeats = []
next_id = 1

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/style.css')
def serve_css():
    return render_template('style.css'), 200, {'Content-Type': 'text/css'}

@app.route('/main.js')
def serve_js():
    return render_template('main.js'), 200, {'Content-Type': 'application/javascript'}

@app.route('/exeat', methods=['GET'])
def list_exeats():
    return jsonify(exeats)

@app.route('/exeat', methods=['POST'])
def create_exeat():
    global next_id
    data = request.get_json()
    # Basic validation
    try:
        first = data['first_name']
        surname = data['surname']
        level = int(data['level'])
        line = int(data['chapel_line'])
        seat = int(data['chapel_seat'])
        absent_start = data['absent_start']
        absent_end = data.get('absent_end', absent_start)
        # parse to ensure valid date
        datetime.strptime(absent_start, '%Y-%m-%d')
        datetime.strptime(absent_end, '%Y-%m-%d')
    except Exception as e:
        return jsonify({"error": "Invalid data format", "details": str(e)}), 400

    record = {
        "id": next_id,
        "first_name": first,
        "surname": surname,
        "level": level,
        "chapel_line": line,
        "chapel_seat": seat,
        "absent_start": absent_start,
        "absent_end": absent_end
    }
    exeats.append(record)
    next_id += 1
    return jsonify(record), 201

@app.route('/exeat/<int:exeat_id>', methods=['PUT'])
def update_exeat(exeat_id):
    data = request.get_json()
    for rec in exeats:
        if rec['id'] == exeat_id:
            # update fields
            rec['first_name'] = data.get('first_name', rec['first_name'])
            rec['surname'] = data.get('surname', rec['surname'])
            rec['level'] = int(data.get('level', rec['level']))
            rec['chapel_line'] = int(data.get('chapel_line', rec['chapel_line']))
            rec['chapel_seat'] = int(data.get('chapel_seat', rec['chapel_seat']))
            rec['absent_start'] = data.get('absent_start', rec['absent_start'])
            rec['absent_end'] = data.get('absent_end', rec['absent_end'])
            return jsonify(rec)
    return jsonify({"error": "Record not found"}), 404

@app.route('/exeat/<int:exeat_id>', methods=['DELETE'])
def delete_exeat(exeat_id):
    global exeats
    new_list = [rec for rec in exeats if rec['id'] != exeat_id]
    if len(new_list) == len(exeats):
        return jsonify({"error": "Record not found"}), 404
    exeats = new_list
    return jsonify({"message": "Deleted"}), 200

if __name__ == '__main__':
    # Use port 3000 as per your requirement
    app.run(host='0.0.0.0', port=3000, debug=True)