import pymssql
import os

# os用来和操作系统进行交互，包括处理文件和目录。
class ConnectionManager:
    # 构造函数
    def __init__(self):
        self.server_name = os.getenv("Server")  # getenv(key)——返回环境变量中key对应的value
        self.db_name = os.getenv("DBName")
        self.user = os.getenv("UserID")
        self.password = os.getenv("Password")
        self.conn = None

    def create_connection(self):
        # python中也有try-catch模块
        try:
            # print(self.server_name)
            # print(self.db_name)
            # print(self.user)
            # print(self.password)
            # conn相当于当前类的一个属性；三方库pymssql.connect()执行后返回一个manager的东西给到conn，最后返回self.conn
            self.conn = pymssql.connect(server=self.server_name, user=self.user, password=self.password, database=self.db_name)
        except pymssql.Error as db_err:  # db_err相当于是pymssql.Error
            print("Database Programming Error in SQL connection processing! ")
            sqlrc = str(db_err.args[0])
            print("Exception code: " + str(sqlrc)) # 用+连接当中无space，用,连接当中有space
        return self.conn

    def close_connection(self):
        try:
            # 个人理解：这里close()其实是pymssql.connect()执行后返回对象所拥有的一个方法
            self.conn.close()
        except pymssql.Error as db_err:
            print("Database Programming Error in SQL connection processing! ")
            sqlrc = str(db_err.args[0])
            print("Exception code: " + str(sqlrc))
