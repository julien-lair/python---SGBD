from PySide6.QtCore import *
from PySide6.QtWidgets import *
from PySide6.QtGui import *
import socket
import hashlib
import json

class MainWindow(QMainWindow):
  
        
    def __init__(self):
        super().__init__()
        self.connected = False


        self.setWindowTitle("Client - Base de donnée")
        self.setMinimumSize(QSize(500,800))
        self.setMaximumSize(QSize(500,800))
        self.move(200,30)

        self.label_top = QLabel(f"Client - Base de donnée") 

        self.host_label = QLabel("Adresse du serveur:")
        self.host_input = QLineEdit()
        self.host_input.setFixedWidth(300)
        self.host_layout = QHBoxLayout()
        self.host_layout.addWidget(self.host_label)
        self.host_layout.addWidget(self.host_input)


        self.port_label = QLabel("Port:")
        self.port_input = QLineEdit()
        self.port_input.setFixedWidth(300)
        self.port_layout = QHBoxLayout()
        self.port_layout.addWidget(self.port_label)
        self.port_layout.addWidget(self.port_input)


        self.user_label = QLabel("Identifiant:")
        self.user_input = QLineEdit()
        self.user_input.setFixedWidth(300)
        self.user_layout = QHBoxLayout()
        self.user_layout.addWidget(self.user_label)
        self.user_layout.addWidget(self.user_input)


        self.password_label = QLabel("Mot de passe:")
        self.password_input = QLineEdit()
        self.password_input.setFixedWidth(300)
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_layout = QHBoxLayout()
        self.password_layout.addWidget(self.password_label)
        self.password_layout.addWidget(self.password_input)

        
        self.sql_label = QLabel("Commande SQL:")
        self.sql_input = QLineEdit()
        self.sql_input.setFixedWidth(300)
        self.sql_input.setFixedHeight(50)
        self.sql_layout = QHBoxLayout()
        self.sql_layout.addWidget(self.sql_label)
        self.sql_layout.addWidget(self.sql_input)


        self.button_execute = QPushButton("Éxécuter")
        self.button_execute.clicked.connect(self.execute)

        layout = QVBoxLayout()
        layout.addWidget(self.label_top)
        layout.addSpacing(20)
        layout.addLayout(self.host_layout)
        layout.addLayout(self.port_layout)
        layout.addLayout(self.user_layout)
        layout.addLayout(self.password_layout)
        layout.addLayout(self.sql_layout)
        layout.addWidget(self.button_execute)
        


        

        self.status_label = QLabel("Status:")
        self.status_layout = QHBoxLayout()
        self.status_layout.addWidget(self.status_label)


        self.message_label = QLabel("Message:")
        self.message_layout = QHBoxLayout()
        self.message_layout.addWidget(self.message_label)


        self.data_label = QLabel("Data:")
        self.data_table = QTableWidget()
        self.data_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        
        self.data_layout = QVBoxLayout()
        self.data_layout.addWidget(self.data_label)
        self.data_layout.addWidget(self.data_table)
        self.data_layout.addStretch()


        secondLayout = QVBoxLayout()
        secondLayout.addLayout(self.status_layout)
        secondLayout.addLayout(self.message_layout)
        secondLayout.addLayout(self.data_layout)
        secondLayout.addStretch()


        secondGroup = QGroupBox("Résultat")
        secondGroup.setLayout(secondLayout)

        main_layout = QVBoxLayout()
        main_layout.addLayout(layout)
        main_layout.addWidget(secondGroup)

        container = QWidget()
        container.setLayout(main_layout)
        
        self.setCentralWidget(container)


    def execute(self):
        host = self.host_input.text()
        port = self.port_input.text()
        identifiant = self.user_input.text()
        password = self.password_input.text()
        sql = self.sql_input.text()

        if self.connected:
                data = self.send_sql_request(self.server,sql)
                self.setResult(data)
                return
        

        if host != "" and port != "" and identifiant != "" and password != "" and sql != "":
            server = self.connect_to_serveur(host,int(port))
            self.server = server
            if self.connected == False:
                if(self.auth_to_serveur(server, identifiant, password)):
                    self.connected = True
                    #l'utilisateur est bien connecté
                    self.disable_input_connection_info()
                    data = self.send_sql_request(server,sql)
                    self.setResult(data)
                

    def connect_to_serveur(self,host,port)->socket:
        try:
            serveur = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
            serveur.connect((host, port))
        except Exception:
            self.statusBar().showMessage("Échec de connexion", 3000)
        return serveur 
    

    def auth_to_serveur(self,serveur : socket, username, password) -> bool:
        password_hash = hashlib.sha512(password.encode('utf-8')).hexdigest()
        creds = {"user":username, "password": password_hash}
        serveur.send(json.dumps(creds).encode())
        data = serveur.recv(4096).decode()
        if json.loads(data)["statut"] == "sucess":
            return True
        else:
            print(json.loads(data)["message"])
            self.statusBar().showMessage("Échec de connexion", 3000)
            return False
        
    def disable_input_connection_info(self):
        self.host_input.setDisabled(True)
        self.port_input.setDisabled(True)
        self.user_input.setDisabled(True)
        self.password_input.setDisabled(True)

    def send_sql_request(self,serveur, sql) -> json:
        serveur.send(sql.encode())
        data = serveur.recv(4096).decode()
        return json.loads(data)

    def setResult(self, data : json):
        self.status_label.setText(f'Status:      {data["statut"]}')
        self.message_label.setText(f'Message:       {data["message"]}')
        if data["statut"] == "sucess" and data["data"] != None:
            self.update_table(data["action"], json.loads(data["data"]))
        else:
            #pas de table à afficher, on reste le tableau
            self.reset_table() 

    def update_table(self,action, data):
        if action == "DESCRIBE":
            self.data_table.setRowCount(len(json.loads(data["colonnes"])))
            self.data_table.setColumnCount(2)
            compteur_ligne = 0
            for elem in json.loads(data["colonnes"]):
                colonne_name = elem["colonne"]
                colonne_type = elem["type"]
                self.data_table.setItem(compteur_ligne, 0, QTableWidgetItem(colonne_name))
                self.data_table.setItem(compteur_ligne, 1, QTableWidgetItem(colonne_type))
                compteur_ligne += 1
            
            self.data_table.setHorizontalHeaderLabels(["Nom","Type"])

        elif action == "SELECT":
            self.data_table.setRowCount(len(data["data"]))
            self.data_table.setColumnCount(len(data["colonnes"]))
            self.data_table.setHorizontalHeaderLabels(data["colonnes"])

            compteur_ligne = 0
            for elem in data["data"]:
                compteur_col = 0
                for col in elem:
                    self.data_table.setItem(compteur_ligne, compteur_col, QTableWidgetItem(f"{col}"))
                    compteur_col += 1
                compteur_ligne += 1
    def reset_table(self):
        self.data_table.setRowCount(0)
        self.data_table.setColumnCount(0)


if __name__ == '__main__':
    app = QApplication()
    window = MainWindow()
    
    window.show()
    app.exec()