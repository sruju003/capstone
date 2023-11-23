import face_recognition
import cv2

# Load known images and encode faces
known_image1 = face_recognition.load_image_file("vishnu.jpg")
# known_image2 = face_recognition.load_image_file("known_person2.jpg")
known_encoding1 = face_recognition.face_encodings(known_image1)[0]
# known_encoding2 = face_recognition.face_encodings(known_image2)[0]

# Create an array of known face encodings and corresponding names
known_face_encodings = [known_encoding1]
known_face_names = ["Vishnu"]

# Open the camera
video_capture = cv2.VideoCapture(0)
print("Webcam initialized")


while True:
    # Capture each frame from the video feed
    ret, frame = video_capture.read()

    # Find all face locations and face encodings in the current frame
    face_locations = face_recognition.face_locations(frame)
    face_encodings = face_recognition.face_encodings(frame, face_locations)

    # Loop through each face found in the frame
    for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
        # Check if the face matches any known face
        matches = face_recognition.compare_faces(known_face_encodings, face_encoding)

        name = "Unknown"

        # If a match is found, use the name of the known face
        if True in matches:
            first_match_index = matches.index(True)
            name = known_face_names[first_match_index]

        # Draw a rectangle and label around the face
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
        font = cv2.FONT_HERSHEY_DUPLEX
        cv2.putText(frame, name, (left + 6, bottom - 6), font, 0.5, (255, 255, 255), 1)

    # Display the resulting frame
    cv2.imshow('Video', frame)

    # Break the loop when 'q' key is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the video feed and close all windows
video_capture.release()
cv2.destroyAllWindows()
print("Script completed")