import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import Qt
import paho.mqtt.client as mqtt
from mqtt_init import *

DEFAULT_RELAY_TOPIC = 'pr/home/button_123_YY/sts'         
GATE_STATUS_TOPIC    = 'pr/home/gate_123_YY/status'       
clientname = "IOT_relay_simulator"
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
        else:
            print("MQTT not connected, failed to publish.")

    def on_connect(self, client, userdata, flags, rc):
        global CONNECTED
        CONNECTED = True
        print("Relay Simulator: Connected")

    def on_disconnect(self, client, userdata, rc):
        global CONNECTED
        CONNECTED = False
        print("Relay Simulator: Disconnected")

class RelaySimulator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MQTT Relay Simulator (Gate)")
        self.setGeometry(900, 100, 400, 350)

        font = QFont()
        font.setPointSize(14)

        # Topic input GUI
        self.topic_input = QLineEdit(DEFAULT_RELAY_TOPIC)
        self.topic_input.setFont(font)
        self.topic_input.setPlaceholderText("Enter MQTT relay topic...")
        
        self.topic_button = QPushButton("Set Topic")
        self.topic_button.setFont(font)
        self.topic_button.clicked.connect(self.change_topic)

        self.status_label = QLabel("Gate is OPEN")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setFont(font)

        self.relay_image = QLabel()
        self.relay_image.setAlignment(Qt.AlignCenter)

        layout = QVBoxLayout()
        layout.addWidget(self.topic_input)
    
        layout.addWidget(self.relay_image)
        layout.addWidget(self.status_label)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.mqtt = MqttClient(self.on_message)
        self.mqtt.connect()
        self.mqtt.subscribe(DEFAULT_RELAY_TOPIC)

        self.set_gate_image(open=True)

    def change_topic(self):
        new_topic = self.topic_input.text().strip()
        if new_topic:
            self.mqtt.subscribe(new_topic)

    def set_gate_image(self, open):
        image_path = "gate_open.png" if open else "gate_closed.png"
        pixmap = QPixmap(image_path).scaled(250, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.relay_image.setPixmap(pixmap)

        gate_status = "gate_open" if open else "gate_closed"
        self.status_label.setText("Gate is OPEN" if open else "Gate is CLOSED")

        self.mqtt.publish(GATE_STATUS_TOPIC, gate_status)

    def on_message(self, client, userdata, msg):
        message = msg.payload.decode().strip()
        print("MQTT Received:", message)
        if "value:1" in message:
            self.set_gate_image(open=False)
        elif "value:0" in message:
            self.set_gate_image(open=True)

app = QApplication(sys.argv)
window = RelaySimulator()
window.show()
app.exec_()
