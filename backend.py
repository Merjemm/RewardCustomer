from flask import Flask, request, jsonify
import sqlite3
import requests
import xml.etree.ElementTree as ET
from flask_cors import CORS
app = Flask(__name__)
CORS(app)


conn = sqlite3.connect('purchases.db')
cursor = conn.cursor()
cursor.execute('''
    CREATE 
    TABLE IF NOT EXISTS purchases (
        id INTEGER PRIMARY KEY,
        agent_email TEXT,
        customer_id TEXT,
        purchase_amount REAL
    )
''')
conn.commit()
conn.close()


def fetch_customer_data(customer_id):
    try:
        
        api_url = f'https://www.crcind.com/csp/samples/SOAP.Demo.cls?soap_method=FindPerson&id={customer_id}'
        result = client.service.FindPerson(id=customer_id)
    return result
        
        if response.status_code == 200:
            root = ET.fromstring(response.content)
            customer_name = root.find(".//Name").text
            customer_email = root.find(".//Email").text
            
            if customer_name and customer_email:
                return {"customer_name": customer_name, "customer_email": customer_email}
        return None
    except Exception as e:
        app.logger.error(f"Failed to fetch data from the API for customer_id: {customer_id}. Error: {str(e)}")
        return None


@app.route('/dataadmission', methods=['POST'])
def data_admission():
    try:
        data = request.get_json()
        agent_email = data.get('agent_email')
        customer_id = data.get('customer_id')
        purchase_amount = data.get('purchase_amount')

        
        conn = sqlite3.connect('purchases.db')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO purchases (agent_email, customer_id, purchase_amount) VALUES (?, ?, ?)',
                       (agent_email, customer_id, purchase_amount))
        conn.commit()
        conn.close()

        return jsonify({"message": "Data admitted successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route('/enriched_data', methods=['GET'])
def enriched_data():
    try:
        conn = sqlite3.connect('purchases.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM purchases')
        rows = cursor.fetchall()
        conn.close()

        enriched_entries = []

        for row in rows:
            agent_email, customer_id, purchase_amount = row

            customer_data = fetch_customer_data(customer_id)
            if customer_data:
                enriched_entry = {
                    "agent_email": agent_email,
                    "customer_id": customer_id,
                    "purchase_amount": purchase_amount,
                    **customer_data
                }
                enriched_entries.append(enriched_entry)

        return jsonify(enriched_entries)
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route('/dataadmission', methods=['PATCH'])
def edit_entry():
    try:
        data = request.get_json()
        agent_email = data.get('agent_email')
        customer_id = data.get('customer_id')
        purchase_amount = data.get('purchase_amount')

        
        conn = sqlite3.connect('purchases.db')
        cursor = conn.cursor()
        cursor.execute('UPDATE purchases SET agent_email = ?, purchase_amount = ? WHERE customer_id = ?',
                       (agent_email, purchase_amount, customer_id))
        conn.commit()
        conn.close()

        return jsonify({"message": "Data updated successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    app.run(port=5000)