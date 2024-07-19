from flask import Flask, request, jsonify
import ipinfo
import math

app = Flask(__name__)

# Global variable to store the latest received data
latest_data = {}

# Function to calculate battery level and battery life (placeholders)
def calculate_battery_level(voltage):
    return voltage * 10

def calculate_battery_life(voltage):
    return voltage * 20

# Placeholder for the bme_prediction function
def bme_prediction(temperature, humidity, pressure, gas_resistance, gas_index, meas_index):
    return 1

# Function to get IP information
def get_ip_info(ip_address):
    try:
        access_token = '72511d15b2d4da'  # Replace with your ipinfo access token
        handler = ipinfo.getHandler(access_token)
        details = handler.getDetails(ip_address)
        
        city = details.city
        region = details.region
        country = details.country
        latitude, longitude = details.loc.split(',')

        return {
            "country": country,
            "region": region,
            "city": city,
            "postal": details.postal,
            "latitude": latitude,
            "longitude": longitude,
            "timezone": details.timezone,
            "isp": details.org,
            "asn": details.org.split(' ')[0]  # Assuming the ASN is the first part of org
        }
    except Exception as e:
        print(f"Error fetching IP info: {e}")
        return {"error": "Unable to fetch IP information"}

@app.route('/')
def home():
    # Display the latest received data
    return jsonify(latest_data)

@app.route('/data', methods=['POST'])
def receive_data():
    global latest_data
    try:
        data = request.get_json()
        print(f"Received data: {data}")

        # Extract gateway_data
        gateway_data = data.get('gateway_data', {})
        module_data_list = data.get('module_data', [])

        # Process gateway_data
        processed_gateway_data = process_data(gateway_data, "g")

        # Get IP information if IP address is present in gateway_data
        ip_address = gateway_data.get('Ip_address')
        if ip_address:
            ip_info = get_ip_info(ip_address)
            processed_gateway_data.update(ip_info)
        else:
            ip_info = {}

        # Process each module data
        processed_module_data_list = [process_data(module_data, "m", gateway_data.get('Module_id')) for module_data in module_data_list]

        latest_data = {
            "message": "Data received and processed",
            "gateway_data": processed_gateway_data,
            "module_data": processed_module_data_list,
            "ip_info": ip_info
        }

        print(f"Response data: {latest_data}")
        return jsonify(latest_data), 200
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500

def process_data(data, data_type, gateway_module_id=None):
    module_id = data.get('Module_id')
    temperature = float(data.get('Temperature', 0))
    humidity = float(data.get('Humidity', 0))
    pressure = float(data.get('Pressure', 0))
    gas_resistance = float(data.get('Gas_resistance', 0))
    status = data.get('Status')
    gas_index = float(data.get('Gas_index', 0))
    meas_index = float(data.get('Meas_index', 0))
    weight = float(data.get('Weight', 0))
    voltage = float(data.get('Voltage', 0))
    ax = float(data.get('Ax', 0))
    ay = float(data.get('Ay', 0))
    az = float(data.get('Az', 0))
    gx = float(data.get('Gx', 0))
    gy = float(data.get('Gy', 0))
    gz = float(data.get('Gz', 0))
    num_sim = data.get('Num_sim', None)

    acc = math.sqrt(ax**2 + ay**2 + az**2)
    ang_veloc = math.sqrt(gx**2 + gy**2 + gz**2)

    acc_threshold = 1.0
    ang_veloc_threshold = 1.0
    stability = 0 if acc > acc_threshold or ang_veloc > ang_veloc_threshold else 1

    batt_level = calculate_battery_level(voltage)
    batt_life = calculate_battery_life(voltage)
    prediction = bme_prediction(temperature, humidity, pressure, gas_resistance, gas_index, meas_index)

    processed_data = {
        "module_id": module_id,
        "temperature": temperature,
        "humidity": humidity,
        "pressure": pressure,
        "gas_resistance": gas_resistance,
        "status": status,
        "gas_index": gas_index,
        "meas_index": meas_index,
        "weight": weight,
        "voltage": voltage,
        "ax": ax,
        "ay": ay,
        "az": az,
        "gx": gx,
        "gy": gy,
        "gz": gz,
        "num_sim": num_sim,
        "acc": acc,
        "ang_veloc": ang_veloc,
        "stability": stability,
        "batt_level": batt_level,
        "batt_life": batt_life,
        "prediction": prediction,
        "gateway_module_id": gateway_module_id
    }

    return processed_data

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
