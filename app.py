from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

@app.route("/option-chain", methods=["GET"])
def get_option_chain():
    stock_symbol = request.args.get("stock")
    target_param = request.args.get("targets")  # Format: 8300CE,8700PE,8000CE,9000PE

    if not stock_symbol or not target_param:
        return jsonify({"error": "Missing stock or targets parameter"}), 400

    targets = []
    for t in target_param.split(","):
        if len(t) > 2:
            targets.append({"strike": t[:-2], "type": t[-2:]})

    # Step 1: Get company name
    search_url = f"https://service.upstox.com/search/open/v1/?query={stock_symbol}&segments=EQ&records=1&pageNumber=1"
    headers = {
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0"
    }

    try:
        search_resp = requests.get(search_url, headers=headers, timeout=10)
        search_resp.raise_for_status()
        search_data = search_resp.json()

        if not search_data.get("success") or not search_data.get("data", {}).get("searchList"):
            return jsonify({"error": "Failed to fetch symbol from Upstox search"}), 500

        company_name = search_data["data"]["searchList"][0]["attributes"]["name"]
        formatted_name = company_name.lower().replace(" ", "-")
        option_chain_url = f"https://upstox.com/option-chain/{formatted_name}/"

        # Step 2: Fetch HTML page
        html_resp = requests.get(option_chain_url, headers=headers, timeout=10)
        html_resp.raise_for_status()

        soup = BeautifulSoup(html_resp.text, "html.parser")
        option_data = []

        rows = soup.select("table.table-auto tbody tr")

        for row in rows:
            cols = row.find_all("td")
            if len(cols) == 19 or len(cols) == 20:
                strike = cols[9].select_one("div span.font-medium")
                if not strike:
                    continue
                strike_value = strike.text.strip().replace(",", "")
                ce_ltp = cols[8].text.strip()
                pe_ltp = cols[10].text.strip()
                ce_oi = cols[6].text.strip()
                pe_oi = cols[12].text.strip()

                for target in targets:
                    if target["strike"] == strike_value:
                        option_data.append({
                            "strike": strike_value,
                            "type": target["type"],
                            "ltp": ce_ltp if target["type"] == "CE" else pe_ltp,
                            "oi": ce_oi if target["type"] == "CE" else pe_oi,
                        })

        # Match the original target order
        sorted_data = [
            d for t in targets
            for d in option_data
            if d["strike"] == t["strike"] and d["type"] == t["type"]
        ]

        return jsonify(sorted_data)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
