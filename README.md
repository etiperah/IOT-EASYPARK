# Smart Parking System - EazyPark 🚗

A smart IoT-based parking management system that detects parking spot occupancy using a distance sensor and publishes real-time data using MQTT. The project includes a graphical user interface (GUI) for monitoring and control, and stores data in an SQLite database for future analysis.

## 💡 Project Overview

EazyPark is designed to automate the monitoring of parking space availability. By simulating a distance sensor, the system detects whether a parking spot is occupied or free. This information is published via MQTT to a central broker and visualized in a PyQt5-based GUI.

## 🛠️ Technologies Used

| Tool / Library     | Purpose                                      |
|--------------------|----------------------------------------------|
| **Python**         | Main programming language                    |
| **PyQt5**          | GUI development                              |
| **paho-mqtt**      | MQTT communication                           |
| **SQLite**         | Local database to store distance readings    |
| **HiveMQ**         | MQTT broker used for testing and monitoring  |

## 📦 Project Structure

```
IOTpro/
│
├── MonitorGUI.py         # Main GUI application for monitoring
├── DataHandler.py        # Handles saving distance data to SQLite
├── distance_sensor.py    # Simulates the distance sensor with MQTT
├── button_simulator.py   # Simulates a button to control parking status
├── mqtt_init.py          # MQTT configuration (broker, topics, etc.)
└── distance_data.db      # SQLite database (auto-created)
```

## 🔌 How It Works

1. **Distance Sensor Simulator**
   - Generates simulated distance values.
   - Publishes values to an MQTT topic.
   - If distance is below a defined threshold, the spot is considered **occupied**.

2. **MQTT Communication**
   - All components connect to an MQTT broker (e.g., HiveMQ).
   - Messages are published and subscribed in real-time.

3. **GUI Application**
   - Displays real-time status of the parking spot (Occupied/Free).
   - Shows a visual LED indicator.
   - Saves every distance reading to a local database (`distance_data.db`).

4. **Data Logging**
   - All distance values are logged with a timestamp.
   - Useful for historical data analysis.

## 🧪 Example Topics

- **Distance Publishing Topic:** `pr/home/5976397/parking`
- **Button Command Topic:** `pr/home/button_123_YY/sts`
- **Gate Status Topic:** `pr/home/gate_123_YY/status`

## 🚀 Getting Started

1. Clone the project
2. Run `MonitorGUI.py` to launch the main interface
3. Optionally run `distance_sensor.py` or `button_simulator.py` to simulate devices

## 📚 Future Improvements

- Add real-time analytics dashboard
- Integrate with a mobile application
- Add support for multiple parking spots
- Implement alert system for illegal parking

## 📄 License

This project is part of a university IoT course and is provided for educational purposes.

---
