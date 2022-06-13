import sys
sys.path.append("../util/*") # 这里..就是返回上级directory；有了这个path就能到时候本地import了
sys.path.append("../db/*")
from util.Util import Util # 这里import的Util应该指的是class name而不是filename
from db.ConnectionManager import ConnectionManager
import pymssql


class Caregiver:  # 你可以生成实例去更新到db，也可以生成实例然后去db中取对应数据
    def __init__(self, username, password=None, salt=None, hash=None): # 依赖外部参数传入去初始化；password默认None
        self.username = username
        self.password = password
        self.salt = salt
        self.hash = hash

    # getters —— 用来验证login的
    # 用户只需要输入username和password，然后我们根据username从db中取出salt，和输入的password一起算出hash，再和db中hash比较
    def get(self):  # py语法很灵活，这里甚至不需要定义方法的返回类型
        cm = ConnectionManager()  # 因为import了ConnectionManager这个类，所以可以直接用
        conn = cm.create_connection()
        cursor = conn.cursor(as_dict=True)

        get_caregiver_details = "SELECT Salt, Hash FROM Caregivers WHERE Username = %s"
        try:
            # 自己理解：通过terminal触发Caregiver实例生成，通过该实例的getter触发远程Azure运行SQL获取数据，并将数据塞进实例中
            # 好处是SQL语句是通过Caregiver实例的属性来动态生成的，更灵活——也就是通过py来定制化SQL操作
            cursor.execute(get_caregiver_details, self.username)
            for row in cursor:
                curr_salt = row['Salt']
                curr_hash = row['Hash']  # 从select的结果中提取hash和salt
                calculated_hash = Util.generate_hash(self.password, curr_salt) # 这是基于用户输入的password计算出的hash
                if not curr_hash == calculated_hash:
                    cm.close_connection()
                    return None  # 如果密码不正确，返回None
                else:
                    self.salt = curr_salt  # 【！！】感觉这里不赋值也没事，但说不动之后要用
                    self.hash = calculated_hash
                    # 【！！】感觉这里需要close_connection
                    return self  # 这里getter返回的不是具体某个值，而是实例本身，实例自身的hash和salt两个属性已经被更新了
        except pymssql.Error:
            print("Error occurred when getting Caregivers")
            cm.close_connection()
        # cm.close_connection()  # 要是发生了except还会走这里吗？
        return None

    def get_username(self):
        return self.username

    def get_salt(self):
        return self.salt

    def get_hash(self):
        return self.hash

    def save_to_db(self):
        cm = ConnectionManager()
        conn = cm.create_connection()
        cursor = conn.cursor()

        add_caregivers = "INSERT INTO Caregivers VALUES (%s, %s, %s)"
        try:
            cursor.execute(add_caregivers, (self.username, self.salt, self.hash))
            # you must call commit() to persist your data if you don't set autocommit to True
            conn.commit()
        except pymssql.Error as db_err:
            print("Error occurred when inserting Caregivers")
            sqlrc = str(db_err.args[0])  # str函数可以把对象强制转化成为string类型
            print("Exception code: " + str(sqlrc))
            cm.close_connection()
        cm.close_connection()

    # Insert availability with parameter date d
    def upload_availability(self, d):  # 我理解availability这张表格是表示医生其有空日期的；这张表格是和医生有关的，所以放在医生这个类里
        cm = ConnectionManager()
        conn = cm.create_connection()
        cursor = conn.cursor()

        add_availability = "INSERT INTO Availabilities VALUES (%s , %s)"
        try:
            cursor.execute(add_availability, (d, self.username))
            # you must call commit() to persist your data if you don't set autocommit to True
            conn.commit()
            print("Availability uploaded!")
        except pymssql.Error:  # 【？？】上传违反key规则的tuple会触发这里吗？——经过试验，会的
            print("Error occurred when updating caregiver availability")
            cm.close_connection()
        cm.close_connection()  # 【！！】经过试验发现重复close_connection不要紧；这里没return也不要紧
