from auth_manager import AuthManager

def main():
    auth = AuthManager()
    #serveur TCP
    # écoute à l'infinie, si quelqu'un se connecte alors : 
    #Auth 
    auth.new_connection()
    if(auth.isConnected):
        print("Bienvenue sur le serveur :)")
    else:
        return 1
    return 0
if __name__ == "__main__":
    main()