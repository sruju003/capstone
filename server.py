from flask import Flask, request, jsonify, render_template, send_from_directory, redirect, url_for
from pymongo import MongoClient, server_api
import face_recognition
import pickle, base64
from io import BytesIO
from PIL import Image
import numpy as np
import os

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

# Create or get a database
db = client['button_clicks_db']

# Create or get a collection
#button_clicks = db['button_clicks'] #choose a specific collection based on the user.


@app.route('/update_count', methods=['POST'])
def update_count():
    data = request.get_json()
    button_id = data.get('button_id')
    click_count = data.get('click_count')
    user_name = data.get('user_name')
    sessional_count = data.get('sessional_count')

    # Dynamically create or use the user-specific collection
    collection_name = f"button_clicks_{user_name}"
    button_clicks = db[collection_name]

    if button_id and click_count is not None:
        button_count = button_clicks.find_one({'buttonId': button_id})
        if button_count:  # Update the click count for the existing button
            count = button_count.get('count', 0)
            count += click_count
            button_clicks.update_one(
                {'buttonId': button_id},
                {'$set': {'count': count, 'sessional_count': sessional_count}},
                upsert=True
            )
        else:  # Create a new button if it doesn't exist
            button_clicks.update_one(
                {'buttonId': button_id},
                {'$set': {'count': click_count, 'sessional_count': sessional_count}},
                upsert=True
            )

        return jsonify({'message': 'Click count updated successfully'})
    else:
        return jsonify({'message': 'Invalid data'}), 400


@app.route('/data', methods=['POST'])
def get_data():
    if request.method == 'POST':
        data = request.get_json()
        user_name = data.get('authenticatedUser')
        collection_name = f"button_clicks_{user_name}"
        button_clicks = db[collection_name]

        # Retrieve all button clicks
        all_button_clicks = list(button_clicks.find())

        # Print all button clicks and their counts
        for button_click in all_button_clicks:
            button_id = button_click.get('buttonId')
            count = button_click.get('count', 0)
            print(f"Button ID: {button_id}, Count: {count}")

        # Find the button with the maximum count
        max_count_button = button_clicks.find_one(sort=[('count', -1), ('buttonId', 1)], limit=1)

        if max_count_button:
            id=max_count_button.get('buttonId')
            max_count = max_count_button.get('count', 0)
            return jsonify({
                'authenticatedUser': user_name,
                'id': id,
                'message': max_count
            })
        else:
            return jsonify({
                'authenticatedUser': user_name,
                'message': 'No button clicks found'
            })

    else:
        return jsonify({'message': 'Invalid request method'}), 400


@app.route('/get_count/<user_name>/<button_id>', methods=['GET'])
def get_count(user_name, button_id):
    # Dynamically access the user-specific collection
    collection_name = f"button_clicks_{user_name}"
    button_clicks = db[collection_name]

    # Retrieve the count from the user-specific collection
    button_count = button_clicks.find_one({'buttonId': button_id})
    if button_count:
        count = button_count.get('count', 0)
    else:
        count = 0

    return jsonify({'user_name': user_name, 'button_id': button_id, 'click_count': count})


@app.route('/get_all_counts', methods=['GET'])
def get_all_counts():
    all_button_counts = {}

    # Iterate over each user's collection
    for user_name in db.list_collection_names():

        # Dynamically access the user-specific collection
        collection_name = user_name
        button_clicks = db[collection_name]

        # Retrieve the counts for all buttons from the user-specific collection
        user_counts = {}
        for button_record in button_clicks.find({}):
            button_id = button_record.get('buttonId')
            click_count = button_record.get('count', 0)
            user_counts[button_id] = click_count

        all_button_counts[user_name] = user_counts

    return jsonify(all_button_counts)


def load_face_encodings(file_path):
    with open(file_path, 'rb') as file:
        known_face_encodings, names = pickle.load(file)
    return known_face_encodings, names

known_faces_file = "known_faces.pkl"
known_face_encodings, known_face_names = load_face_encodings(known_faces_file)

# Function to recognize faces from real-time camera feed
def recognize_realtime_face(image_data):
    try:
        # Decode base64 image data
        image_bytes = base64.b64decode(image_data.split(',')[1])

        # Open the image using Pillow
        img = Image.open(BytesIO(image_bytes))

        # Convert the image to RGB format
        img = img.convert('RGB')

        # Find face locations and encodings
        face_locations = face_recognition.face_locations(np.array(img))
        face_encodings = face_recognition.face_encodings(np.array(img), face_locations)

        if not face_encodings:
            return None

        # Compare with the encodings of known faces
        for face_encoding in face_encodings:
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
            if True in matches:
                first_match_index = matches.index(True)
                name = known_face_names[first_match_index]
                return name

        return None

    except Exception as e:
        print(e)
        return None
    
@app.route('/')
def authenticate_camera():
    return render_template('camera.html')

@app.route('/authenticate_realtime', methods=['POST'])
def authenticate_realtime():
    try:
        image_data = request.get_json()['image_data']
        authenticated_user = recognize_realtime_face(image_data)

        if authenticated_user:
            print(f"Real-time authentication successful for user: {authenticated_user}")
            return jsonify({'authenticated_user': authenticated_user})
        else:
            print("Real-time authentication failed")
            return jsonify({'message': 'Authentication failed'}), 403

    except Exception as e:
        print(e)
        return jsonify({'message': 'An error occurred during real-time authentication'}), 500

@app.route('/index')
def index():
    authenticated_user = request.args.get('authenticated_user')
    return render_template('gpayappland.html', authenticated_user=authenticated_user)

def save_face_encodings(file_path, image_paths, names):
    known_face_encodings = []

    for image_path in image_paths:
        # Load the image
        known_image = face_recognition.load_image_file(image_path)

        # Encode the face
        face_encoding = face_recognition.face_encodings(known_image)[0]
        known_face_encodings.append(face_encoding)

    # Save the encodings and corresponding names to a file
    with open(file_path, 'wb') as file:
        pickle.dump((known_face_encodings, names), file)

known_faces_file = "known_faces.pkl"
known_face_encodings, known_face_names = load_face_encodings(known_faces_file)
known_image_filenames = ["vishnu.jpg", "keerthi.jpg", "samyam.jpg", "srujana.jpg"]
known_names = ["Vishnu", "Keerthi", "Samyam", "Srujana"]

@app.route('/encode_reference', methods=['GET'])
def encode_reference():
    try:
        # known_image_filenames = ["vishnu.jpg", "keerthi.jpg"]
        # known_names = ["Vishnu", "Keerthi"]

        # Save the fresh encodings to the file
        save_face_encodings(known_faces_file, known_image_filenames, known_names)

        return jsonify({'message': 'Reference image encoded successfully'})

    except Exception as e:
        print(e)
        return jsonify({'message': 'An error occurred during encoding'}), 500

known_image_paths = [os.path.join(app.config['ENCODING_FOLDER'], filename) for filename in known_image_filenames]
    
app.config['STATIC_URL_PATH'] = '/static'
app.config['STATIC_FOLDER'] = 'static'
app.config['ENCODING_PATH'] = '/pics'
app.config['ENCODING_FOLDER'] = 'pics'

if __name__ == '__main__':
    app.run(debug=True)
