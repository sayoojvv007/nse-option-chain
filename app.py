from flask import Flask, jsonify
import requests

app = Flask(__name__)

@app.route("/option-chain/<symbol>")
def option_chain(symbol):
    url = f"https://www.nseindia.com/api/option-chain-v3?type=Equity&symbol={symbol}&expiry=31-Jul-2025"

    headers = {
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64)",
        "accept-language": "en-GB,en;q=0.9",
        "referer": "https://www.nseindia.com/option-chain"
    }

    cookies = {
        "nseappid": "<PASTE_HERE>",
        "bm_sv": "<PASTE_HERE>",
        "bm_mi": "<PASTE_HERE>",
        "aka_a2": "<PASTE_HERE>"
    }

    session = requests.Session()
    session.get("https://www.nseindia.com", headers=headers)
    response = session.get(url, headers=headers, cookies=cookies)

    return jsonify(response.json())

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
