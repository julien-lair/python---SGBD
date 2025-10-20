import unittest
from sql_parser import Parser
from table import Table
from ShuntingYard import ShuntingYard
from database import Database
import os 
from result import resultAPI

class TestParser(unittest.TestCase):
    # Test de la class Parser()
    #     
    def setUp(self):
        #avant chaque apelle de test
        self.parser = Parser()
    
    def tearDown(self):
        # après chaque apelle de test
        self.parser = None
    
    def test_CREATE(self):
        sql = "CREATE TABLE users (id SERIAL, prenom TEXT, age INT);"
        self.parser.parse(sql)
        self.assertTrue(self.parser.expressionValide)
        self.assertEqual(self.parser.action, "CREATE")
        self.assertEqual(self.parser.table, "users")
        self.assertEqual(self.parser.columns_name, ["id", "prenom", "age"])
        self.assertEqual(self.parser.columns_type, ["SERIAL", "TEXT", "INT"])
    
    def test_DROP(self):
        sql = "DROP TABLE users;"
        self.parser.parse(sql)
        self.assertTrue(self.parser.expressionValide)
        self.assertEqual(self.parser.action, "DROP")
        self.assertEqual(self.parser.table, "users")

    def test_INSERT_1(self):
        sql = "INSERT INTO users VALUES ('julien', 23, False),('Pierre',28,True);"
        self.parser.parse(sql)
        self.assertTrue(self.parser.expressionValide)
        self.assertEqual(self.parser.action, "INSERT")
        self.assertEqual(self.parser.table, "users")
        self.assertEqual(self.parser.values, [["'julien'","23","False"],["'Pierre'","28","True"]])

    def test_INSERT_2(self):
        sql = "INSERT INTO users (prenom,age,inscrit) VALUES ('julien', 23, False),('Pierre',28,True);"
        self.parser.parse(sql)
        self.assertTrue(self.parser.expressionValide)
        self.assertEqual(self.parser.action, "INSERT")
        self.assertEqual(self.parser.table, "users")
        self.assertEqual(self.parser.values, [["'julien'","23","False"],["'Pierre'","28","True"]])
        self.assertEqual(self.parser.columns_name, ["prenom","age","inscrit"])

    def test_SELECT_1(self):
        sql = "SELECT * FROM users;"
        self.parser.parse(sql)
        self.assertTrue(self.parser.expressionValide)
        self.assertEqual(self.parser.action, "SELECT")
        self.assertEqual(self.parser.table, "users")
        self.assertEqual(self.parser.columns_name, ["*"])
    
    def test_SELECT_2(self):
        sql = "SELECT name,age FROM users;"
        self.parser.parse(sql)
        self.assertTrue(self.parser.expressionValide)
        self.assertEqual(self.parser.action, "SELECT")
        self.assertEqual(self.parser.table, "users")
        self.assertEqual(self.parser.columns_name, ["name","age"])

    def test_SELECT_3(self):
        sql = "SELECT name,age FROM users WHERE (age > 25 OR age <= 32) AND name != 'julien';"
        self.parser.parse(sql)
        self.assertTrue(self.parser.expressionValide)
        self.assertEqual(self.parser.action, "SELECT")
        self.assertEqual(self.parser.table, "users")
        self.assertEqual(self.parser.columns_name, ["name","age"])
        self.assertTrue(isinstance(self.parser.where, ShuntingYard))

    def test_SELECT_4(self):
        sql = "SELECT name,age FROM users WHERE (age > 25 OR age <= 32) AND name != 'julien' ORDER BY name ASC;"
        self.parser.parse(sql)
        self.assertTrue(self.parser.expressionValide)
        self.assertEqual(self.parser.action, "SELECT")
        self.assertEqual(self.parser.table, "users")
        self.assertEqual(self.parser.columns_name, ["name","age"])
        self.assertTrue(isinstance(self.parser.where, ShuntingYard))
        self.assertEqual(self.parser.orderBy, {"colonne":"name","order": "ASC"})

    def test_SELECT_5(self):
        sql = "SELECT name,age FROM users WHERE (age > 25 OR age <= 32) AND name != 'julien' ORDER BY name DESC LIMIT 3;"
        self.parser.parse(sql)
        self.assertTrue(self.parser.expressionValide)
        self.assertEqual(self.parser.action, "SELECT")
        self.assertEqual(self.parser.table, "users")
        self.assertEqual(self.parser.columns_name, ["name","age"])
        self.assertTrue(isinstance(self.parser.where, ShuntingYard))
        self.assertEqual(self.parser.orderBy, {"colonne":"name","order": "DESC"})
        self.assertEqual(self.parser.limit, 3)

    def test_SELECT_6(self):
        sql = "SELECT name,age FROM users WHERE (age > 25 OR age <= 32) AND name != 'julien' ORDER BY name DESC LIMIT 4 OFFSET 2;"
        self.parser.parse(sql)
        self.assertTrue(self.parser.expressionValide)
        self.assertEqual(self.parser.action, "SELECT")
        self.assertEqual(self.parser.table, "users")
        self.assertEqual(self.parser.columns_name, ["name","age"])
        self.assertTrue(isinstance(self.parser.where, ShuntingYard))
        self.assertEqual(self.parser.orderBy, {"colonne":"name","order": "DESC"})
        self.assertEqual(self.parser.limit, 4)
        self.assertEqual(self.parser.offset, 2)

    def test_SELECT_7(self):
        sql = "SELECT name,age FROM users WHERE (age > 25 OR age <= 32) AND name != 'julien' ORDER BY name DESC OFFSET 2;"
        self.parser.parse(sql)
        self.assertTrue(self.parser.expressionValide)
        self.assertEqual(self.parser.action, "SELECT")
        self.assertEqual(self.parser.table, "users")
        self.assertEqual(self.parser.columns_name, ["name","age"])
        self.assertTrue(isinstance(self.parser.where, ShuntingYard))
        self.assertEqual(self.parser.orderBy, {"colonne":"name","order": "DESC"})
        self.assertEqual(self.parser.offset, None)
    
    def test_DESCRIBE(self):
        sql = "DESCRIBE users;"
        self.parser.parse(sql)
        self.assertTrue(self.parser.expressionValide)
        self.assertEqual(self.parser.action, "DESCRIBE")
        self.assertEqual(self.parser.table, "users")

    def test_UPDATE(self):
        sql = "UPDATE users SET name='julien', age =45 WHERE _id > 6;"
        self.parser.parse(sql)
        self.assertTrue(self.parser.expressionValide)
        self.assertEqual(self.parser.action, "UPDATE")
        self.assertEqual(self.parser.table, "users")
        self.assertTrue(isinstance(self.parser.where, ShuntingYard))
        self.assertEqual(self.parser.update, [{"colonne":"name","value":"'julien'"},{"colonne":"age","value":"45"}])
        
    def test_DELETE(self):
        sql = "DELETE FROM users WHERE age > 2;"
        self.parser.parse(sql)
        self.assertTrue(self.parser.expressionValide)
        self.assertEqual(self.parser.action, "DELETE")
        self.assertEqual(self.parser.table, "users")
        self.assertTrue(isinstance(self.parser.where, ShuntingYard))

    def test_ERROR_1(self):
        sql = "SELECT * FROM users"
        self.parser.parse(sql)
        self.assertEqual(self.parser.expressionValide, False)

    def test_ERROR_2(self):
        sql = ""
        self.parser.parse(sql)
        self.assertEqual(self.parser.expressionValide, False)
    
    def test_ERROR_3(self):
        sql = "SELECTO * FROM users;"
        self.parser.parse(sql)
        self.assertEqual(self.parser.expressionValide, False)
    
    def test_ERROR_4(self):
        sql = "CREATE TABLE users (id SERIAL, prenom TEXT, age);"
        self.parser.parse(sql)
        self.assertEqual(self.parser.expressionValide, False)

class TestWhere(unittest.TestCase):
    # Test de la class ShuntingYard() responsable des pile pour le WHERE
    #     
    def setUp(self):
        #avant chaque apelle de test
        self.parser = Parser()

    def tearDown(self):
        # après chaque apelle de test
        self.parser = None

    def test_WHERE_1(self):
        sql = "SELECT * FROM users WHERE age < 28;"
        self.parser.parse(sql)
        self.assertTrue(self.parser.expressionValide)
        self.assertEqual(self.parser.where.RPN, ["age<28"])

    def test_WHERE_1(self):
        sql = "SELECT * FROM users WHERE age < 28 OR prenom = 'julien';"
        self.parser.parse(sql)
        self.assertTrue(self.parser.expressionValide)
        self.assertEqual(self.parser.where.RPN, ["age<28","prenom='julien'","OR"])
    
    def test_WHERE_2(self):
        sql = "SELECT * FROM users WHERE ((age >= 18 AND age < 30) OR (age > 60 AND city = 'Paris')) AND ((role = 'admin' OR role = 'manager') AND active = 1) AND (points != 0 AND score >= 50);"
        self.parser.parse(sql)
        self.assertTrue(self.parser.expressionValide)
        self.assertEqual(self.parser.where.RPN, ["age>=18", "age<30", "AND", "age>60", "city='Paris'", "AND", "OR", "role='admin'", "role='manager'", "OR", "active=1", "AND", "AND", "points!=0", "score>=50", "AND", "AND"])

class TestTable(unittest.TestCase):
    # Test de la class Table() 
    #     
    def setUp(self):
        #avant chaque apelle de test
        self.parser = Parser()
        self.database = Database()

    def tearDown(self):
        # après chaque apelle de test
        self.parser = None

    def test_CREATE(self):
        sql = "CREATE TABLE unittest (name TEXT, age INT, admin BOOL);"
        self.parser.parse(sql)
        self.database.create_table(self.parser.table, self.parser.columns_name, self.parser.columns_type)
        self.assertTrue(os.path.exists(os.path.dirname(__file__)+"/data/unittest.db"))
        for table in self.database.tables:
                    if table.name == "unittest":
                        self.assertEqual(table.columns,[{'colonne': '_id', 'type': 'SERIAL'}, {'colonne': 'name', 'type': 'TEXT'}, {'colonne': 'age', 'type': 'INT'}, {'colonne': 'admin', 'type': 'BOOL'}])
        
    def test_INSERT_1(self):
        sql = "INSERT INTO unittest VALUES ('julien',23,True),('Pierre',29,False);"
        self.parser.parse(sql)
        self.database.insert_table(self.parser)
        for table in self.database.tables:
            if table.name == "unittest":
                self.assertEqual(table.lines,[[{'colonne': '_id', 'type': 'SERIAL', 'value': 0}, {'colonne': 'name', 'type': 'TEXT', 'value': 'julien'}, {'colonne': 'age', 'type': 'INT', 'value': '23'}, {'colonne': 'admin', 'type': 'BOOL', 'value': 'True'}], [{'colonne': '_id', 'type': 'SERIAL', 'value': 1}, {'colonne': 'name', 'type': 'TEXT', 'value': 'Pierre'}, {'colonne': 'age', 'type': 'INT', 'value': '29'}, {'colonne': 'admin', 'type': 'BOOL', 'value': 'False'}]])

    def test_DELETE_1(self):
        sql = "DELETE FROM unittest;"
        self.parser.parse(sql)
        self.database.insert_table(self.parser)
        for table in self.database.tables:
            if table.name == "unittest":
                self.assertEqual(table.lines,[])

    def test_INSERT_2(self):
        sql = "INSERT INTO unittest (admin,name,age) VALUES (True,'julien',23,);"
        self.parser.parse(sql)
        self.database.insert_table(self.parser)
        for table in self.database.tables:
            if table.name == "unittest":
                self.assertEqual(table.lines,[[{'colonne': '_id', 'type': 'SERIAL', 'value': 0}, {'colonne': 'name', 'type': 'TEXT', 'value': 'julien'}, {'colonne': 'age', 'type': 'INT', 'value': '23'}, {'colonne': 'admin', 'type': 'BOOL', 'value': 'True'}]])

    def test_DELETE_2(self):
        sql = "DELETE FROM unittest WHERE _id = 0;"
        self.parser.parse(sql)
        self.database.insert_table(self.parser)
        for table in self.database.tables:
            if table.name == "unittest":
                self.assertEqual(table.lines,[])

    def test_UPDATE(self):
        sql = "UPDATE unittest SET admin = False WHERE age < 30;"
        self.parser.parse(sql)
        self.database.update_table(self.parser)
        for table in self.database.tables:
            if table.name == "unittest":
                self.assertEqual(table.lines,[[{'colonne': '_id', 'type': 'SERIAL', 'value': 0}, {'colonne': 'name', 'type': 'TEXT', 'value': 'julien'}, {'colonne': 'age', 'type': 'INT', 'value': '23'}, {'colonne': 'admin', 'type': 'BOOL', 'value': 'False'}]])

    def test_DROP(self):
        sql = "DROP TABLE unittest;"
        self.parser.parse(sql)
        self.database.drop_table(self.parser.table)
        self.assertTrue(not os.path.exists(os.path.dirname(__file__)+"/data/unittest.db"))
        

"""
class TestTable(unittest.TestCase):
    
    def test_table_creation(self):
        self.create_test_table()
        table = Table(self.test_db_path)
        
        self.assertEqual(table.name, "users")
        self.assertEqual(len(table.columns), 3)
        self.assertEqual(table.columns[0]["colonne"], "_id")
"""



def run_tests():
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # On apelle nos différents class de tests
    suite.addTests(loader.loadTestsFromTestCase(TestParser))
    suite.addTests(loader.loadTestsFromTestCase(TestWhere))
    suite.addTests(loader.loadTestsFromTestCase(TestTable))
    
    # on éxécute tous les tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result.wasSuccessful()


if __name__ == '__main__':
    if run_tests():
        exit(0)
    else:
        exit(1)