import sys, random, socket
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont
import paho.mqtt.client as mqtt
from mqtt_init import *

DISTANCE_TOPIC = 'pr/home/5976397/parking'
BUTTON_TOPIC = 'pr/home/button_123_YY/sts'
UPDATE_INTERVAL = 5000
clientname = f"IOT_distance_sensor_{random.randint(0, 999999)}"
CONNECTED = False

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "Unavailable"

class MqttClient():
    def __init__(self):
        self.client = mqtt.Client(clientname)
        self.client.username_pw_set(username, password)
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect

    def connect(self):
        self.client.connect(broker_ip, int(broker_port))
        self.client.loop_start()

    def on_connect(self, client, userdata, flags, rc):
        global CONNECTED
        CONNECTED = True
        print("Connected to MQTT broker")

    def on_disconnect(self, client, userdata, rc):
        global CONNECTED
        CONNECTED = False
        print("Disconnected from MQTT broker")

    def publish(self, topic, message):
        if CONNECTED:
            self.client.publish(topic, message)
        else:
            print("MQTT not connected")

class DistanceSensor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Distance Sensor Monitor")
        self.setGeometry(100, 100, 500, 350)
        self.setMinimumSize(400, 300)

        self.mqtt = MqttClient()
        self.mqtt.connect()

        font = QFont("Segoe UI", 13)
        field_height = 50
        style_common = """
            QLineEdit {
                border-radius: 8px;
                padding: 10px;
                border: 2px solid #ccc;
                background-color: #f8f8f8;
            }
        """

        # IP Address
        self.ip_label = QLineEdit(get_local_ip())
        self.ip_label.setReadOnly(True)
        self.ip_label.setFont(font)
        self.ip_label.setFixedHeight(field_height)
        self.ip_label.setStyleSheet(style_common)

        # Topic Display
        self.topic_display = QLineEdit(DISTANCE_TOPIC)
        self.topic_display.setReadOnly(True)
        self.topic_display.setFont(font)
        self.topic_display.setFixedHeight(field_height)
        self.topic_display.setStyleSheet(style_common)
        self.topic_display.setToolTip("Copy this topic into MQTT GUI to subscribe")

        # Distance Display
        self.distance_display = QLineEdit()
        self.distance_display.setReadOnly(True)
        self.distance_display.setFont(font)
        self.distance_display.setAlignment(Qt.AlignCenter)
        self.distance_display.setFixedHeight(field_height)
        self.distance_display.setStyleSheet(style_common)

        # Status Display
        self.status_display = QLineEdit()
        self.status_display.setReadOnly(True)
        self.status_display.setFont(font)
        self.status_display.setAlignment(Qt.AlignCenter)
        self.status_display.setFixedHeight(field_height)
        self.status_display.setStyleSheet(style_common)

        # Layout
        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignLeft)
        form.addRow("MQTT Topic:", self.topic_display)
        form.addRow("Distance (cm):", self.distance_display)
        

        container = QWidget()
        container.setLayout(form)
        self.setCentralWidget(container)

        # Timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.measure)
        self.timer.start(UPDATE_INTERVAL)

    def measure(self):
        distance = random.randint(5, 100)
        is_taken = distance < 30
        status = "occupied" if is_taken else "free"

        # Update GUI
        self.distance_display.setText(f"{distance} cm")
        self.status_display.setText(status.capitalize())

        # צבע לפי סטטוס
        if is_taken:
            self.status_display.setStyleSheet("""
                QLineEdit {
                    background-color: #ffc0c0;
                    color: #800000;
                    border-radius: 8px;
                    border: 2px solid #ccc;
                    padding: 10px;
                }
            """)
        else:
            self.status_display.setStyleSheet("""
                QLineEdit {
                    background-color: #c0ffc0;
                    color: #006600;
                    border-radius: 8px;
                    border: 2px solid #ccc;
                    padding: 10px;
                }
            """)

        # MQTT Publish
        self.mqtt.publish(DISTANCE_TOPIC, str(distance))
        self.mqtt.publish(BUTTON_TOPIC, "value:1" if is_taken else "value:0")

        print(f"Published to {DISTANCE_TOPIC}: {distance}")
        print(f"Published to {BUTTON_TOPIC}: {'value:1' if is_taken else 'value:0'}")

app = QApplication(sys.argv)
win = DistanceSensor()
win.show()
app.exec_()
