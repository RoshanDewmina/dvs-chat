import requests

API_URL = "http://localhost:8000/ask"

def main():
    print("Welcome to the InfluxDB CLI chatbot. Type your Flux query or 'exit' to quit.")
    while True:
        user_input = input("You: ")
        if user_input.lower() in ("exit", "quit"):
            break
        response = requests.post(API_URL, json={"query": user_input})
        if response.status_code == 200:
            print("Bot:", response.json()["results"])
        else:
            print("Error:", response.json().get("detail", "Unknown error"))

if __name__ == "__main__":
    main()