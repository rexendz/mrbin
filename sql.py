import pymysql


class SQLServer:
    def __init__(self, host="localhost", user="root", passwd="", database="mrbin"):
        self.conn = pymysql.connect(
            host=host, 
            user=user, 
            passwd=passwd, 
            database=database)
        self.query = ''
        self.curr = self.conn.cursor()

    def getLength(self):
        return len(self.readAll())

    def insert(self, name, uid, pts, bottle, table="Users"):
        self.query = """
        INSERT INTO {} (Name, RFID_UID, Incentives, Bottle_Deposited) VALUES ('{}', {}, {}, {})
        """.format(table, name, uid, pts, bottle)
        self.execute()
        self.commit()

    def update(self, Where, WhereVal, Set, SetVal, table="Users"):
        self.query= """
        UPDATE {}
        SET {} = {}
        WHERE {} = {}
        """.format(table, Set, SetVal, Where, WhereVal)
        self.execute()
        self.commit()

    def updateId(self, table="Users"):
        self.query = "SET @count = 0;"
        self.execute()
        self.query = "UPDATE {} SET id = @count:= @count + 1;".format(table)
        self.execute()
        self.commit()

    def updateIncrement(self, table="Users"):
        nextId = (int(self.getLength())+1)
        self.query = "ALTER TABLE {} AUTO_INCREMENT = {};".format(table, nextId)
        self.execute()
        self.commit()

    def delete(self, Where, WhereVal, table="Users"):
        if Where == "Name":
            self.query = "DELETE FROM {} WHERE {} = '{}'".format(table, Where, WhereVal)
        else:
            self.query = "DELETE FROM {} WHERE {} = {}".format(table, Where, WhereVal)
        self.execute()
        self.commit()

    def deleteLatest(self):
        self.delete("ID", self.getLength())

    def execute(self):
        self.curr.execute(self.query)

    def getResult(self):
        return self.curr.fetchall()
    
    def commit(self):
        self.conn.commit()

    def readAll(self, table="Users"):
        self.query = "SELECT * FROM {}".format(table)
        self.execute()
        return self.curr.fetchall()

    def findUid(self, uid, table="Users"):
        self.query = """
        SELECT * FROM {} WHERE RFID_UID = {}
        """.format(table, uid)
        self.execute()
        return self.curr.fetchall()

    def findID(self, id, table="Users"):
        self.query = """
        SELECT * FROM {} WHERE id = {}
        """.format(table, id)
        self.execute()
        return self.curr.fetchall()

    def modifyRecordByID(self, id, name, rfid, pts, bottles, table="Users"):
        self.query = "UPDATE {} SET Name = '{}', RFID_UID = {}, Incentives = {}, Bottle_Deposited = {} WHERE id = {};".format(table, name, rfid, pts, bottles, id)
        self.execute()
        self.commit()

    def modifyRecordByName(self, name, rfid, pts, table="Users"):
        self.query = "UPDATE {} SET Name = '{}', RFID_UID = {}, Incentives = {} WHERE Name = {};".format(table, name, rfid, pts, name)
        self.execute()
        self.commit()

    def updateIncentives(self, id, pts, bottle, table="Users"):
        self.query = "UPDATE {} SET Incentives = {} WHERE id = {};".format(table, pts, id)
        self.execute()
        self.query = "UPDATE {} SET Bottle_Deposited = {} WHERE id = {};".format(table, bottle, id)
        self.execute()
        self.commit()
        print("Updated")

    def uidIsExisting(self, uid):
        return len(self.findUid(uid))

    def close(self):
        self.conn.close()
        print("SQL Closed")
    

if __name__ == "__main__":
    sql = SQLServer("localhost", "root", passwd="", database="mrbin")
    for rows in sql.findUid(int(0x563D0346)):
        _, name, uid, pts = rows
    print("Welcome, " + name)
    print("Points: " + str(pts))
    sql.close()
