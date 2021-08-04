import requests
import json
import pyttsx3
import speech_recognition as sr
import re
import threading
import time
API_KEY = "tuRAnx-rbFSp"
project_token = "twJxrZDa5fQ0"
run_token = "tMXrJ8EvdKv_"



    # creates class for all covid parshub data
class Data:
    def __init__(self, api_key, project_token):
        self.api_key = api_key
        self.project_token = project_token
        self.params = {
            "api_key": self.api_key
        }
        self.data = self.get_data()
        
    # accesses parsehub server for covid data
    def get_data(self):
        response = requests.get(f'https://www.parsehub.com/api/v2/projects/{self.project_token}/last_ready_run/data', params=self.params)
        data = json.loads(response.text)
        return data

    # defines class for total cases and grabs values for covid cases
    def get_total_cases(self):
        data = self.data['total']
    
        for content in data:
            if content['name'] == "Coronavirus Cases:":
                return content['value']

    # defines class for covid deaths and gras values for covid deaths
    def get_total_deaths(self):
         data = self.data['total']

         for content in data:
            if content['name'] == "Deaths:":
                return content['value']

            return "0"
        
    # defines class for country data and gathers each country data     
    def get_country_data(self, country):
        data = self.data["country"]

        for content in data:
            if content['name'].lower() == country.lower():
                return content

        return "0"
    
    # defines class list of countries and puts all countries in a dectornary in alphibetical order
    def get_list_of_countries(self):
        countries = []
        for country in self.data['country']:
            countries.append(country['name'].lower())

        return countries
        
    #initializes a new run on the parshub servers
    def update_data(self):
        response = requests.post(f'http://www.parsehub.com/api/v2/projects/{self.project_token}/run', params=self.params)
        old_data = self.data


    #creates a string to get updated data from server without interupting the voice control
        def poll():
            time.sleep(0.1)
            old_data = self.data
            while True:
                new_data = self.get_data()
                if new_data != old_data:
                    self.data = new_data
                    print("Data updated")
                    break
                time.sleep(5)

        t = threading.Thread(target=poll)
        t.start()
                
    # Gives audio output for data
def speak(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

    # Takes user audio input and prints Exception: if command isnt recognized
def get_audio():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        audio = r.listen(source)
        said = ""

        try:
            said = r.recognize_google(audio)
        except Exception as e:
            print("Exception:", str(e))

    return said.lower()

    # All verbal commands for retreiving covid data from server and stopping program
def main():
    print("Started Program")
    data = Data(API_KEY, project_token)
    END_PHRASE = "stop"
    country_list = data.get_list_of_countries()

    TOTAL_PATTERNS = {
                    re.compile("[\w\s]+ total [\w\s]+ cases"): data.get_total_cases,
                    re.compile("[\w\s]+ total cases"): data.get_total_cases,
                    re.compile("[\w\s]+ total [\w\s]+ deaths"): data.get_total_deaths,
                    re.compile("[\w\s]+ total deaths"): data.get_total_deaths
                    }
    COUNTRY_PATTERNS = {
                    re.compile("[\w\s]+ cases [\w\s]+"): lambda country: data.get_country_data(country)['total_cases'],
                    re.compile("[\w\s]+ deaths [\w\s]+"): lambda country: data.get_country_data(country)['total_deaths'],
                    }

    # Update command pulls current covid data from parshub server 
    UPDATE_COMMAND = "update"
    
    while True:
        print("Listening...")
        text = get_audio()
        print(text)
        result = None

        for pattern, func in COUNTRY_PATTERNS.items():
            if pattern.match(text):
                words = set(text.split(" "))
                for country in country_list:
                    if country in words:
                        result = func(country)
                        break
        
        for pattern, func in TOTAL_PATTERNS.items():
            if pattern.match(text):
                result = func()
                break
            
    # gives verbal confrimation of update command 
        if text == UPDATE_COMMAND:
            result = "Data is being updated. This may take a moment!"
            data.update_data()
        
        if result:
            speak(result)

        if text.find(END_PHRASE) != -1:
            print("Exit")
            break
main()
