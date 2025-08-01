import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import paho.mqtt.client as mqtt
from mqtt_init import *
from PyQt5.QtCore import Qt

DEFAULT_BUTTON_TOPIC = 'pr/home/button_123_YY/sts'
RELAY_TOPIC = 'pr/home/relay_123_YY/sts'
clientname = "IOT_button_simulator"
CONNECTED = False

class MqttClient():
    def __init__(self, on_message_callback):
        self.client = mqtt.Client(clientname)
        self.client.username_pw_set(username, password)
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.client.on_message = on_message_callback
        self.current_topic = None

    def connect(self):
        self.client.connect(broker_ip, int(broker_port))
        self.client.loop_start()

    def subscribe(self, topic):
        if self.current_topic:
            self.client.unsubscribe(self.current_topic)
        self.current_topic = topic
        self.client.subscribe(topic)
        print(f"Subscribed to: {topic}")

    def publish(self, topic, message):
        if CONNECTED:
            self.client.publish(topic, message)
            print(f"Published to {topic}: {message}")

    def on_connect(self, client, userdata, flags, rc):
        global CONNECTED
        CONNECTED = True
        print("Button Simulator: Connected")

    def on_disconnect(self, client, userdata, rc):
        global CONNECTED
        CONNECTED = False
        print("Button Simulator: Disconnected")

class ButtonSimulator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MQTT Parking Button")
        self.setGeometry(500, 100, 350, 200)

        font = QFont()
        font.setPointSize(14)

        # Topic input field
        self.topic_input = QLineEdit(DEFAULT_BUTTON_TOPIC)
        self.topic_input.setFont(font)
        self.topic_input.setPlaceholderText("Enter MQTT topic...")

        # Button to confirm topic
        self.topic_button = QPushButton("Set Topic")
        self.topic_button.setFont(font)
        self.topic_button.clicked.connect(self.change_topic)

        # Button status label
        self.status_label = QLabel("free")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setFont(font)

        # Visual parking button
        self.button = QPushButton("Parking button")
        self.button.setFont(font)
        self.button.setStyleSheet("background-color: green; color: white;")
        self.button.setEnabled(False)

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.topic_input)

        layout.addWidget(self.button)
        layout.addWidget(self.status_label)

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

        self.mqtt = MqttClient(self.on_message)
        self.mqtt.connect()
        self.mqtt.subscribe(DEFAULT_BUTTON_TOPIC)

    def change_topic(self):
        new_topic = self.topic_input.text().strip()
        if new_topic:
            self.mqtt.subscribe(new_topic)

    def update_button(self, taken):
        if taken:
            self.status_label.setText("occupied")
            self.button.setStyleSheet("background-color: red; color: white;")
            self.mqtt.publish(RELAY_TOPIC, "ATTENTION: OCCUPIED")  # סגור שער
        else:
            self.status_label.setText("free")
            self.button.setStyleSheet("background-color: green; color: white;")
            self.mqtt.publish(RELAY_TOPIC, "ATTENTION: NOW YOU CAN PARK")  # פתח שער

    def on_message(self, client, userdata, msg):
        message = msg.payload.decode().strip()
        print("MQTT Received:", message)
        if "value:1" in message:
            self.update_button(taken=True)
        elif "value:0" in message:
            self.update_button(taken=False)

app = QApplication(sys.argv)
win = ButtonSimulator()
win.show()
app.exec_()
