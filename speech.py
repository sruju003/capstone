import speech_recognition as sr
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions

chrome_path = r'C:\Users\Lenovo\Downloads\chromedriver-win64\chromedriver.exe'

def speech_to_text():
    # Initialize the recognizer
    recognizer = sr.Recognizer()

    with sr.Microphone() as source:
        print("Say something:")
        recognizer.adjust_for_ambient_noise(source)
        print("Listening...")
        audio = recognizer.listen(source)
        print("Analyzing...")

    try:
        # Recognize speech using Google's Speech Recognition
        text = recognizer.recognize_google(audio)
        print("You said:", text)
        return text
    except sr.UnknownValueError:
        print("Could not understand audio")
    except sr.RequestError as e:
        print("Error with the speech recognition service; {0}".format(e))
        return None

def analyze_and_click(text, driver):
    # Analyze the recognized text and perform actions accordingly
    if "scan QR" in text.lower():
        driver.find_element_by_id("scanQR").click()
        print("Clicked Button Scan QR")
    elif "click button 2" in text.lower():
        driver.find_element_by_id("button2").click()
        print("Clicked Button 2")
    else:
        print("No action specified for the recognized text:", text)

if __name__ == "__main__":
    # Set up the Chrome WebDriver with the path to the ChromeDriver executable
    chrome_options = ChromeOptions()
    chrome_options.add_argument("--headless")  # Add this line if you don't want a visible browser window
    driver = webdriver.Chrome(service=ChromeService(executable_path=chrome_path), options=chrome_options)

    # Open the Flask app
    driver.get("http://127.0.0.1:5000/")

    while True:
        # Get the recognized text from speech
        recognized_text = speech_to_text()

        # If text is recognized, analyze and perform actions
        if recognized_text:
            analyze_and_click(recognized_text, driver)
