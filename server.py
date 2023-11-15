from flask import Flask, request, jsonify, render_template
from pymongo import MongoClient

app = Flask(__name__)

# Connect to the MongoDB server
client = MongoClient('mongodb://localhost:27017/')
# Create or get a database
db = client['button_clicks_db']

# Create or get a collection
button_clicks = db['button_clicks']

@app.route('/update_count', methods=['POST'])
def update_count():
    data = request.get_json()
    button_id = data.get('button_id')
    click_count = data.get('click_count')

    if button_id and click_count is not None:
        # Update or insert the count into the MongoDB collection
        button_clicks.update_one(
            {'buttonId': button_id},
            {'$set': {'count': click_count}},
            upsert=True
        )
        return jsonify({'message': 'Click count updated successfully'})
    else:
        return jsonify({'message': 'Invalid data'}), 400

@app.route('/get_count/<button_id>', methods=['GET'])
def get_count(button_id):
    # Retrieve the count from the MongoDB collection
    button_count = button_clicks.find_one({'buttonId': button_id})
    if button_count:
        count = button_count.get('count', 0)
    else:
        count = 0
    return jsonify({'button_id': button_id, 'click_count': count})

@app.route('/get_all_counts', methods=['GET'])
def get_all_counts():
    all_button_counts = {}

    # Retrieve the counts for all buttons from the MongoDB collection
    for button_record in button_clicks.find({}):
        button_id = button_record.get('buttonId')
        click_count = button_record.get('count', 0)
        all_button_counts[button_id] = click_count

    return jsonify(all_button_counts)

@app.route('/')
def index():
    return render_template('gpayapp.html')

if __name__ == '__main__':
    app.run(debug=True)
