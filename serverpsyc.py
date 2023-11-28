from flask import Flask, request, render_template

app = Flask(__name__)



@app.route('/')
def index():
    return render_template('quesown.html')


@app.route('/submit_survey', methods=['POST'])
def submit_survey():
    form_data = request.form
    # Process the received form data
    print(form_data)  # Print form data to console (for demonstration)

    
    return 'Received form data successfully!'  # Response indicating successful submission

if __name__ == '__main__':
    app.run(debug=True)
