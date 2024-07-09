from flask import Flask, request, jsonify
import math
import mysql.connector

app = Flask(__name__)

# Configure database connection
db_config = {
    'user': 'root',
    'password': '',
    'host': 'localhost',
    'database': 'server_database2'
}

# Function to calculate battery level and battery life (placeholders)
def calculate_battery_level(voltage):
    return voltage * 10

def calculate_battery_life(voltage):
    return voltage * 20

# Placeholder for the bme_prediction function
def bme_prediction(temperature, humidity, pressure, gas_resistance, gas_index, meas_index):
    return 1

@app.route('/')
def home():
    return "Hello, Flask!"

@app.route('/data', methods=['POST'])
def receive_data():
    data = request.get_json()

    # Extract gateway_data
    gateway_data = data.get('gateway_data', {})
    module_data_list = data.get('module_data', [])

    # Process gateway_data
    process_data(gateway_data, "g")

    # Process each module data
    for module_data in module_data_list:
        process_data(module_data, "m", gateway_data.get('Module_id'))

    return jsonify({"message": "Data received and processed"}), 200

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

    insert_into_db(data_type, module_id, weight, voltage, batt_level, batt_life, prediction, humidity,
                   temperature, pressure, gas_resistance, status, gas_index, meas_index, stability, ax, ay, az, gx, gy, gz, gateway_module_id, num_sim)

def insert_into_db(data_type, module_id, weight, voltage, batt_level, batt_life, prediction, humidity,
                   temperature, pressure, gas_resistance, status, gas_index, meas_index, stability, ax, ay, az, gx, gy, gz, gateway_module_id, num_sim):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    if data_type == "g":
        cursor.execute("SELECT 1 FROM gateway WHERE module_gtw_id = %s", (module_id,))
        if not cursor.fetchone():
            cursor.execute("""
                INSERT INTO gateway (module_gtw_id) VALUES (%s)
            """, (module_id,))
        
        cursor.execute("""
        INSERT INTO gateway_data (module_gtw_id, ext_humidity, ext_temperature, ext_pressure, status, total_weight, num_sim)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (module_id, humidity, temperature, pressure, status, weight, num_sim))
    else:
        cursor.execute("SELECT 1 FROM module WHERE module_id = %s", (module_id,))
        if not cursor.fetchone():
            cursor.execute("""
                INSERT INTO module (module_id) VALUES (%s)
            """, (module_id,))
        
        cursor.execute("""
        INSERT INTO module_data (module_id, type, weight, voltage, battery_level, battery_life, health, humidity,
        temperature, pressure, gas_resistance, status_bme, gas_index, meas_index, stability, ax, ay, az, gx, gy, gz, module_gtw_id_sender)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (module_id, data_type, weight, voltage, batt_level, batt_life, prediction, humidity,
              temperature, pressure, gas_resistance, status, gas_index, meas_index, stability, ax, ay, az, gx, gy, gz, gateway_module_id))

    conn.commit()
    conn.close()

if __name__ == '__main__':
    app.run(debug=True)
