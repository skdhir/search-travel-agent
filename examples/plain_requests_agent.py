# examples/plain_requests_agent.py
import requests


def main():
    base = "https://api.sanatdhir.com"
    url = f"{base}/api/flights/search"

    params = {
        "origin": "SFO",
        "destination": "LAX",
        "date": "2025-12-01",
    }

    print("🚫 Calling Travel Flights API WITHOUT HAP SDK (looks like unknown/bot)...")
    resp = requests.get(url, params=params)
    print("Status:", resp.status_code)
    try:
        print(resp.json())
    except Exception:
        print(resp.text)


if __name__ == "__main__":
    main()
