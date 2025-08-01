import os
import sys
import random
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import Qt, pyqtSlot, QMetaObject, Q_ARG
import paho.mqtt.client as mqtt
from mqtt_init import *
from data_handler import DataHandler

# Creating Client name - should be unique
global clientname
r = random.randrange(1, 100000)
clientname = "IOT_client-Id-" + str(r)

class Mqtt_client():
    def __init__(self):
        self.broker = ''
        self.topic = ''
        self.port = 0
        self.clientname = ''
        self.username = ''
        self.password = ''
        self.subscribeTopic = ''
        self.publishTopic = ''
        self.publishMessage = ''
        self.on_connected_to_form = ''

    def set_on_connected_to_form(self, on_connected_to_form):
        self.on_connected_to_form = on_connected_to_form

    def set_broker(self, value):
        self.broker = value

    def set_port(self, value):
        self.port = value

    def set_clientName(self, value):
        self.clientname = value

    def set_username(self, value):
        self.username = value

    def set_password(self, value):
        self.password = value

    def on_log(self, client, userdata, level, buf):
        print("log: "+buf)

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("connected OK")
            self.on_connected_to_form()
        else:
            print("Bad connection Returned code=", rc)

    def on_disconnect(self, client, userdata, flags, rc=0):
        print("DisConnected result code "+str(rc))

    def on_message(self, client, userdata, msg):
        topic = msg.topic
        m_decode = str(msg.payload.decode("utf-8", "ignore"))
        print("message from:" + topic, m_decode)

        try:
            value = float(m_decode)
            QMetaObject.invokeMethod(mainwin, "save_distance", Qt.QueuedConnection, Q_ARG(float, value))
        except ValueError:
            pass

        mainwin.subscribeDock.update_mess_win(m_decode)

    def connect_to(self):
        self.client = mqtt.Client(self.clientname, clean_session=True)
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.client.on_log = self.on_log
        self.client.on_message = self.on_message
        self.client.username_pw_set(self.username, self.password)
        print("Connecting to broker ", self.broker)
        self.client.connect(self.broker, self.port)

    def disconnect_from(self):
        self.client.disconnect()

    def start_listening(self):
        self.client.loop_start()

    def stop_listening(self):
        self.client.loop_stop()

    def subscribe_to(self, topic):
        self.client.subscribe(topic)

    def publish_to(self, topic, message):
        self.client.publish(topic, message)

class ConnectionDock(QDockWidget):
    def __init__(self, mc):
        super().__init__()
        self.mc = mc
        self.mc.set_on_connected_to_form(self.on_connected)

        self.eHostInput = QLineEdit(broker_ip)
        self.ePort = QLineEdit(broker_port)
        self.ePort.setValidator(QIntValidator())
        self.eClientID = QLineEdit(clientname)
        self.eUserName = QLineEdit(username)
        self.ePassword = QLineEdit(password)
        self.ePassword.setEchoMode(QLineEdit.Password)
        self.eKeepAlive = QLineEdit("60")
        self.eSSL = QCheckBox()
        self.eCleanSession = QCheckBox()
        self.eCleanSession.setChecked(True)

        self.eConnectbtn = QPushButton("Connect", self)
        self.eConnectbtn.clicked.connect(self.on_button_connect_click)
        self.eConnectbtn.setStyleSheet("background-color: red")

        formLayout = QFormLayout()
        formLayout.addRow("Host", self.eHostInput)
        formLayout.addRow("Port", self.ePort)
        formLayout.addRow("Client ID", self.eClientID)
        formLayout.addRow("User Name", self.eUserName)
        formLayout.addRow("Password", self.ePassword)
        formLayout.addRow("Keep Alive", self.eKeepAlive)
        formLayout.addRow("SSL", self.eSSL)
        formLayout.addRow("Clean Session", self.eCleanSession)
        formLayout.addRow("", self.eConnectbtn)

        widget = QWidget(self)
        widget.setLayout(formLayout)
        self.setTitleBarWidget(widget)
        self.setWidget(widget)
        self.setWindowTitle("Connect")

    def on_connected(self):
        self.eConnectbtn.setStyleSheet("background-color: green")

    def on_button_connect_click(self):
        self.mc.set_broker(self.eHostInput.text())
        self.mc.set_port(int(self.ePort.text()))
        self.mc.set_clientName(self.eClientID.text())
        self.mc.set_username(self.eUserName.text())
        self.mc.set_password(self.ePassword.text())
        self.mc.connect_to()
        self.mc.start_listening()

class PublishDock(QDockWidget):
    def __init__(self, mc):
        super().__init__()
        self.mc = mc

        self.ePublisherTopic = QLineEdit(pub_topic)
        self.eQOS = QComboBox()
        self.eQOS.addItems(["0", "1", "2"])
        self.eRetainCheckbox = QCheckBox()
        self.eMessageBox = QPlainTextEdit()
        self.ePublishButton = QPushButton("Publish", self)
        self.ePublishButton.clicked.connect(self.on_button_publish_click)

        formLayout = QFormLayout()
        formLayout.addRow("Topic", self.ePublisherTopic)
        formLayout.addRow("QOS", self.eQOS)
        formLayout.addRow("Retain", self.eRetainCheckbox)
        formLayout.addRow("Message", self.eMessageBox)
        formLayout.addRow("", self.ePublishButton)

        widget = QWidget(self)
        widget.setLayout(formLayout)
        self.setWidget(widget)
        self.setWindowTitle("Publish")

    def on_button_publish_click(self):
        self.mc.publish_to(self.ePublisherTopic.text(), self.eMessageBox.toPlainText())
        self.ePublishButton.setStyleSheet("background-color: yellow")

class SubscribeDock(QDockWidget):
    def __init__(self, mc):
        super().__init__()
        self.mc = mc

        self.eSubscribeTopic = QLineEdit(sub_topic)
        self.eQOS = QComboBox()
        self.eQOS.addItems(["0", "1", "2"])
        self.eRecMess = QTextEdit()
        self.eSubscribeButton = QPushButton("Subscribe", self)
        self.eSubscribeButton.clicked.connect(self.on_button_subscribe_click)

        formLayout = QFormLayout()
        formLayout.addRow("Topic", self.eSubscribeTopic)
        formLayout.addRow("QOS", self.eQOS)
        formLayout.addRow("Received", self.eRecMess)
        formLayout.addRow("", self.eSubscribeButton)

        widget = QWidget(self)
        widget.setLayout(formLayout)
        self.setWidget(widget)
        self.setWindowTitle("Subscribe")

    def on_button_subscribe_click(self):
        print(self.eSubscribeTopic.text())
        self.mc.subscribe_to(self.eSubscribeTopic.text())
        self.eSubscribeButton.setStyleSheet("background-color: yellow")

    def update_mess_win(self, text):
        self.eRecMess.append(text)

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.mc = Mqtt_client()
        self.data_handler = DataHandler("distance_data.db")

        self.setGeometry(30, 100, 800, 600)
        self.setWindowTitle('Monitor GUI')

        self.connectionDock = ConnectionDock(self.mc)
        self.publishDock = PublishDock(self.mc)
        self.subscribeDock = SubscribeDock(self.mc)

        self.addDockWidget(Qt.TopDockWidgetArea, self.connectionDock)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.publishDock)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.subscribeDock)

    @pyqtSlot(float)
    def save_distance(self, value):
        self.data_handler.insert_distance(value)
        print(f"✅ Distance saved to DB: {value}")

app = QApplication(sys.argv)
mainwin = MainWindow()
mainwin.show()
sys.exit(app.exec_())
