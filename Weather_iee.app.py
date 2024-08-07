import tkinter as tk
from tkinter import messagebox
import requests
import openai

# Function to get weather data
def get_weather(city_name, api_key):
    base_url = "http://api.openweathermap.org/data/2.5/weather?"
    complete_url = base_url + "q=" + city_name + "&appid=" + api_key + "&units=metric"

    response = requests.get(complete_url)
    data = response.json()

    if response.status_code == 200 and "main" in data:
        main = data["main"]
        weather = data["weather"][0]
        wind = data["wind"]

        weather_info = {
            "City": city_name,
            "Temperature": main["temp"],
            "Pressure": main["pressure"],
            "Humidity": main["humidity"],
            "Weather Description": weather["description"],
            "Wind Speed": wind["speed"]
        }

        # Get coordinates for forecast
        coord = data["coord"]
        lat = coord["lat"]
        lon = coord["lon"]

        # Fetch 5-day forecast data
        forecast_url = f"http://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={api_key}&units=metric"
        forecast_response = requests.get(forecast_url)
        forecast_data = forecast_response.json()

        if forecast_response.status_code == 200 and "list" in forecast_data:
            forecast_list = forecast_data["list"]
            forecast_info = []
            for i in range(0, 40, 8):  # 5 days forecast (8 intervals per day)
                day_forecast = forecast_list[i]
                forecast_info.append({
                    "Date": day_forecast["dt_txt"],
                    "Temperature": day_forecast["main"]["temp"],
                    "Weather Description": day_forecast["weather"][0]["description"]
                })
            weather_info["Forecast"] = forecast_info
        else:
            weather_info["Forecast"] = "Forecast Data Not Available"

        return weather_info
    else:
        return {"Error": "City Not Found or API Request Failed"}

# Function to generate health advice using OpenAI
def generate_health_advice(name, age, condition, weather_info, openai_api_key):
    openai.api_key = openai_api_key
    
    prompt = (
        f"Generate personalized health advice for the following user based on the weather conditions:\n\n"
        f"Name: {name}\n"
        f"Age: {age}\n"
        f"Health Condition: {condition}\n"
        f"Weather Info:\n"
        f" - City: {weather_info['City']}\n"
        f" - Temperature: {weather_info['Temperature']}°C\n"
        f" - Weather Description: {weather_info['Weather Description']}\n"
        f" - Humidity: {weather_info['Humidity']}%\n"
        f" - Wind Speed: {weather_info['Wind Speed']} m/s\n\n"
        f"Provide personalized advice on how the current weather may impact individual's health based on their specific diseases, and suggest the best two-line prevention tips for person to stay healthy in this weather."
    )
    
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a health advisor."},
            {"role": "user", "content": prompt}
        ]
    )
    
    return response['choices'][0]['message']['content'].strip()

def get_advice():
    city = city_entry.get()
    name = name_entry.get()
    age = age_entry.get()
    condition = condition_entry.get()
    
    weather_api_key = "d01394afe15b6d7f6a57694cf32e67c1"  # Replace with your actual weather API key
    openai_api_key = "sk-ghryiOcyd97X-jJaUmhszoPElkNIqnZkutM4q44svlT3BlbkFJI5aXo8P_JHLOVDMEFqPbcix25ERwtUjhELLxzIIrwA" 

    weather_info = get_weather(city, weather_api_key)

    if "Error" in weather_info:
        messagebox.showerror("Error", weather_info["Error"])
    else:
        weather_text.delete(1.0, tk.END)
        weather_text.insert(tk.END, 
            f"City: {weather_info['City']}\n"
            f"Temperature: {weather_info['Temperature']}°C\n"
            f"Pressure: {weather_info['Pressure']} hPa\n"
            f"Humidity: {weather_info['Humidity']}%\n"
            f"Weather Description: {weather_info['Weather Description']}\n"
            f"Wind Speed: {weather_info['Wind Speed']} m/s\n"
        )
        
        forecast_text.delete(1.0, tk.END)
        forecast_text.insert(tk.END, "5-Day Forecast:\n")
        for day in weather_info["Forecast"]:
            forecast_text.insert(tk.END, 
                f"{day['Date']}: {day['Temperature']}°C, {day['Weather Description']}\n"
            )
        
        advice = generate_health_advice(name, age, condition, weather_info, openai_api_key)
        advice_text.delete(1.0, tk.END)
        advice_text.insert(tk.END, advice)

# Setting up the GUI
root = tk.Tk()
root.title("Health Advice Based on Weather")

tk.Label(root, text="City:").grid(row=0, column=0, padx=10, pady=10)
city_entry = tk.Entry(root)
city_entry.grid(row=0, column=1, padx=10, pady=10)

tk.Label(root, text="Name:").grid(row=1, column=0, padx=10, pady=10)
name_entry = tk.Entry(root)
name_entry.grid(row=1, column=1, padx=10, pady=10)

tk.Label(root, text="Age:").grid(row=2, column=0, padx=10, pady=10)
age_entry = tk.Entry(root)
age_entry.grid(row=2, column=1, padx=10, pady=10)

tk.Label(root, text="Health Condition:").grid(row=3, column=0, padx=10, pady=10)
condition_entry = tk.Entry(root)
condition_entry.grid(row=3, column=1, padx=10, pady=10)

advice_button = tk.Button(root, text="Get Health Advice", command=get_advice)
advice_button.grid(row=4, column=0, columnspan=2, pady=10)

tk.Label(root, text="Weather Info:").grid(row=5, column=0, columnspan=2)
weather_text = tk.Text(root, height=5, width=50)
weather_text.grid(row=6, column=0, columnspan=2, padx=10, pady=10)

tk.Label(root, text="5-Day Forecast:").grid(row=7, column=0, columnspan=2)
forecast_text = tk.Text(root, height=10, width=50)
forecast_text.grid(row=8, column=0, columnspan=2, padx=10, pady=10)

tk.Label(root, text="Health Advice:").grid(row=9, column=0, columnspan=2)
advice_text = tk.Text(root, height=10, width=50)
advice_text.grid(row=10, column=0, columnspan=2, padx=10, pady=10)

root.mainloop()

