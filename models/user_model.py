import pymysql
from config.config import Config
from flask import jsonify

class UserModel:
    def __init__(self):
        con = Config()
        self.connection = pymysql.connect(
            host=con.MYSQL_HOST,
            user=con.MYSQL_USER,
            password=con.MYSQL_PASSWORD,
            database=con.MYSQL_DB,
            autocommit=True,
            cursorclass=pymysql.cursors.DictCursor
        )
        self.cursor = self.connection.cursor()

    def get_all_users(self):
        self.cursor.execute("SELECT * FROM users")
        return self.cursor.fetchall()

    def add_user(self, email, password_hash):
        if self.cursor.execute('SELECT email FROM users WHERE email = %s', email) > 0:
            return False
        self.cursor.execute('INSERT INTO users (email, password_hash) VALUES (%s, %s)', (email, password_hash))
        self.connection.commit()
        return True

    def get_user_by_email(self, email):
        self.cursor.execute('SELECT * FROM users WHERE email = %s', (email,))
        return self.cursor.fetchone()


    def getflight(self,trip_type,src,dest,departure_date,return_date):
        one_way_query= f"""
            (SELECT fi.departuretimedate, a.name ,fi.arrivaltimedate,fi.price
            FROM airline a
            JOIN flights f ON a.id = f.airlineid
            JOIN flightinstance fi ON fi.flightid = f.id
            WHERE (f.departurelocationid IN (SELECT locationid FROM location WHERE city = %s OR state = %s))
            AND (f.arrivallocationid IN (SELECT locationid FROM location WHERE city = %s OR state = %s))
            AND DATE(fi.departuretimedate) = %s)
        """
        
        params = [src, src, dest, dest, departure_date]
        self.cursor.execute(one_way_query, params)
        one_way_results= self.cursor.fetchall() 
        
        round_trip_result=[]
        if trip_type == 'roundtrip' and return_date:
            round_trip_query = """
            (SELECT fi.departuretimedate, a.name 
            FROM airline a
            JOIN flights f ON a.id = f.airlineid
            JOIN flightinstance fi ON fi.flightid = f.id
            WHERE (f.departurelocationid IN (SELECT locationid FROM location WHERE city = %s OR state = %s))
            AND (f.arrivallocationid IN (SELECT locationid FROM location WHERE city = %s OR state = %s))
            AND DATE(fi.departuretimedate) = %s)
            """
            params = [dest, dest, src, src, return_date]
        
            self.cursor.execute(round_trip_query, params)
            round_trip_result= self.cursor.fetchall()
        print(one_way_results)
        
        return [one_way_results,round_trip_result]
    
    def get_userid_by_email(self,email):
        self.cursor.execute('SELECT userid FROM users WHERE email = %s', (email,))
        return self.cursor.fetchone()        
    
    def updatenames(self,fn,ln,uid):
        # if(len(ln)>0):
        self.cursor.execute('update users set lastname = %s where (userid = %s) ', (ln,uid))
        # if(len(fn)>0):
        self.cursor.execute('update users set firstname = %s where (userid = %s) ', (fn,uid))
        return 
            
    def updatepassword(self,newpass,email):
        self.cursor.execute('update users set password_hash= %s where (email = %s) ', (newpass,email))
        
        
        
            

    
    
        
    
    
    
