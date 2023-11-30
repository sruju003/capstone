from flask import Flask, request, jsonify, redirect, url_for, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('gpayenter.html')

@app.route('/send-numbers', methods=['POST'])
def receive_numbers():
    if request.method == 'POST':
        data = request.get_json()
        received_numbers = data.get('numbers')

        # Process received numbers as needed (e.g., store in a database, perform operations)
        # Example: Print received numbers and redirect to another page
        print('Received numbers:', received_numbers)
        
        # Redirect to another page after processing the numbers
        return redirect(url_for('success_page'))

@app.route('/success')
def success_page():
    return render_template('donepay.html')  # Render your success page here

if __name__ == '__main__':
    app.run(debug=True)
