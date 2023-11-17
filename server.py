from flask import Flask, request, jsonify, render_template
from pymongo import MongoClient, server_api

app = Flask(__name__)

# Connect to the MongoDB server
uri = "mongodb+srv://capstone:capstone1@cluster0.1z4a3y1.mongodb.net/?retryWrites=true&w=majority"

# Create a new client and connect to the server
client = MongoClient(uri, server_api=server_api.ServerApi('1'))

# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

# client = MongoClient('mongodb://127.0.0.1:27017/')


# Create or get a database
db = client['button_clicks_db']

# Create or get a collection
button_clicks = db['button_clicks']


@app.route('/update_count', methods=['POST'])
def update_count():
    data = request.get_json()
    button_id = data.get('button_id')
    click_count = data.get('click_count')
    button_size = data.get('size')

    # Update or insert the count into the MongoDB collection
    if button_id and click_count is not None:
        button_count = button_clicks.find_one({'buttonId': button_id})
        if button_count: # If button exists, then update the value of the click_count by iterating over the existing value
            count = button_count.get('count', 0)
            count += click_count
            button_clicks.update_one(
            {'buttonId': button_id},
            {'$set': {'count': count}},
            upsert=True
        )
        else: # Create a new button if it doesn't exist
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

# # PATCH route for updating user information based on email
# @app.route('/update_button_count/<button_id>', methods=['PATCH'])
# def update_button_count(button_id):
#     try:
#         data = request.get_json()
#         click_count = data.get('click_count')

#         # Find the button
#         button_temp = button_clicks.find_one({'buttonId': button_id})

#         # Update additional fields
#         button_temp['button_id'] = button_temp.get('button_count', 0) + click_count

#         # Save the updated user document
#         button_clicks.update_one({'buttonId': button_id}, {'$set': button_temp})

#         return jsonify({'message': 'Experience, Age, and Data added successfully'}), 200

#     except Exception as error:
#         print(error)
#         return jsonify({'error': 'An error occurred while updating user information'}), 500

@app.route('/')
def index():
    return render_template('gpayapptest.html')

if __name__ == '__main__':
    app.run(debug=True)
