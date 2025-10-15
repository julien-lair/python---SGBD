from server import Server
from database import Database
from result import resultAPI
def main():
    db = Database()
    server = Server("127.0.0.1",1234,db)
    server.start()
if __name__ == "__main__":
    main()