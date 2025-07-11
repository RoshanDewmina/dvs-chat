import requests

API_URL = "http://localhost:8000/chat"

# For direct Flux queries, use /ask endpoint:
# ASK_API_URL = "http://localhost:8000/ask"

def main():
    print("Welcome to the InfluxDB CLI chatbot. Ask your question (e.g., 'Are there any bottlenecks with project Aura?') or type 'exit' to quit.")
    while True:
        user_input = input("You: ")
        if user_input.lower() in ("exit", "quit"):
            break
        response = requests.post(API_URL, json={"question": user_input})
        if response.status_code == 200:
            print("Bot:", response.json().get("answer"))
            details = response.json().get("details")
            if details:
                print("Details:", details)
        else:
            print("Error:", response.json().get("detail", "Unknown error"))

if __name__ == "__main__":
    main()