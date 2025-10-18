import socket
import json 
import tabulate 

HOST = "127.0.0.1"
PORT = 1234

def main():
    serveur = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
    try:
        serveur.connect((HOST, PORT))
        print("Connecté au serveur !")

        connected = True
        while connected:
            cmd = input("> ").strip()
            if cmd.strip() == "exit":
                print("Déconnexion")
                serveur.close()
                connected = False

            if len(cmd) > 0 and cmd.strip() != "exit":
                serveur.send(cmd.encode())
                data = serveur.recv(4096).decode()

                """
                Retour de l'API: 
                {
                    "statut":[succes|error],
                    "action":[inser|update|select|create|drop|delete],
                    "commande":[commande],
                    "code": [code],
                    "message": [message],
                    "data":[null | [...]]
                }
                """
                jsonData = json.loads(data)
                if jsonData["statut"] == "error":
                    print(f'Erreur: {jsonData["code"]} - {jsonData["message"]}')
                elif jsonData["statut"] == "sucess":
                    print(jsonData["message"])
                    if jsonData["data"] != None:
                        dataTable = json.loads(jsonData["data"])
                        if jsonData["action"] == "DESCRIBE":
                            print(dataTable["table_name"])
                            print(tabulate.tabulate(json.loads(dataTable["colonnes"]),{"colonne":"Nom","type":"Type"},tablefmt="grid"))
                        elif jsonData["action"] == "SELECT":
                            print(dataTable["table_name"])
                            print(tabulate.tabulate(dataTable["data"],dataTable["colonnes"],tablefmt="grid"))

 #                            
                        
                        
                        # 
    except ConnectionRefusedError:
        print("Erreur — serveur non lancé ou introuvable.")
    """except Exception as e:
        print("Erreur")
        print(e)
    """
if __name__ == "__main__":
    main()
