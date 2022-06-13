import sys
from model.Vaccine import Vaccine
from model.Caregiver import Caregiver
from model.Patient import Patient
from util.Util import Util
from db.ConnectionManager import ConnectionManager
import pymssql
import datetime


'''
objects to keep track of the currently logged-in user
Note: it is always true that at most one of currentCaregiver and currentPatient is not null
        since only one user can be logged-in at a time
'''
current_patient = None  # 这是global的

current_caregiver = None

# appt_id = 0


def create_patient(tokens):
    # create_patient <username> <password>
    # check 1: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Arguments number incorrect! Please try again!")
        return

    username = tokens[1]
    password = tokens[2]
    # check 2: check if the username has been taken already
    if username_exists_patient(username):  # 【？？】如果这里是true，不应该说明username not taken吗？
        print("Username taken, try again!")
        return

    salt = Util.generate_salt()  # salt和hash都是在这里生成的
    hash = Util.generate_hash(password, salt)

    # create the patient
    try:
        patient = Patient(username, salt=salt, hash=hash)
        # save to caregiver information to our database
        patient.save_to_db()
        print(" *** Account created successfully *** ")
    except pymssql.Error:
        print("Create failed")
        return

def username_exists_patient(username):
    cm = ConnectionManager()
    conn = cm.create_connection()

    select_username = "SELECT * FROM Patients WHERE Username = %s"
    try:
        cursor = conn.cursor(as_dict=True)  # 【？？】啥时候要用as_dict=True
        cursor.execute(select_username, username)
        #  returns false if the cursor is not before the first record or if there are no rows in the ResultSet.
        for row in cursor:
            return row['Username'] is not None
    except pymssql.Error:
        print("Error occurred when checking username")
        cm.close_connection()
    cm.close_connection()
    return False


def create_caregiver(tokens):
    # create_caregiver <username> <password>
    # check 1: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Incorrect argument number! Please try again!")
        return

    username = tokens[1]
    password = tokens[2]
    # check 2: check if the username has been taken already
    if username_exists_caregiver(username):  # 【？？】如果这里是true，不应该说明username not taken吗？
        print("Username taken, try again!")
        return

    salt = Util.generate_salt()  # salt和hash都是在这里生成的
    hash = Util.generate_hash(password, salt)

    # create the caregiver
    try:
        caregiver = Caregiver(username, salt=salt, hash=hash)
        # save to caregiver information to our database
        caregiver.save_to_db()
        print(" *** Account created successfully *** ")
    except pymssql.Error:
        print("Create failed")
        return


def username_exists_caregiver(username):
    cm = ConnectionManager()
    conn = cm.create_connection()

    select_username = "SELECT * FROM Caregivers WHERE Username = %s"
    try:
        cursor = conn.cursor(as_dict=True)  # 【？？】啥时候要用as_dict=True
        cursor.execute(select_username, username)
        #  returns false if the cursor is not before the first record or if there are no rows in the ResultSet.
        for row in cursor:
            return row['Username'] is not None  #【？？】感觉应该改成is not none?
    except pymssql.Error:
        print("Error occurred when checking username")
        cm.close_connection()  # 【？？】连续close两次没问题？
    cm.close_connection()
    return False


def login_patient(tokens):
    # login_patient <username> <password>
    # check 1: if someone's already logged-in, they need to log out first
    global current_patient
    if current_patient is not None or current_caregiver is not None:
        print("Already logged-in!")
        return

    # check 2: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Arguments number incorrect! Please try again!")
        return

    username = tokens[1]
    password = tokens[2]

    patient = None
    try:
        patient = Patient(username, password=password).get()
    except pymssql.Error:  # 【？？】这里仍然需要捕获异常吗？get()函数里不已经捕获了吗？
        print("Error occurred when logging in")

    # check if the login was successful
    if patient is None:
        print("Please try again!")  # 【！！】这里只提示try again是合理的，因为这里无法确定到底是用户名错了还是密码错了
    else:
        print("Patient logged in as: " + username)
        current_patient = patient  # 若登录成功，current_patient获得所有相关信息，包括密码，salt，hash等


def login_caregiver(tokens):
    # login_caregiver <username> <password>
    # check 1: if someone's already logged-in, they need to log out first
    global current_caregiver
    if current_caregiver is not None or current_patient is not None:
        print("Already logged-in!")
        return

    # check 2: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Incorrect argument number! Please try again!")
        return

    username = tokens[1]
    password = tokens[2]

    caregiver = None
    try:
        # 这里返回的caregiver如果一切顺利，各种属性都会有具体值，包括password，salt，hash等
        caregiver = Caregiver(username, password=password).get()
    except pymssql.Error:  # 【？？】这里仍然需要捕获异常吗？get()函数里不已经捕获了吗？
        print("Error occurred when logging in")

    # check if the login was successful
    if caregiver is None:
        print("Please try again!")
    else:
        print("Caregiver logged in as: " + username)
        current_caregiver = caregiver


def search_caregiver_schedule(tokens):  # 该方法无返回值

    global current_caregiver
    global current_patient  # declare this is the global variable outside

    # Check 1: if someone isn't logged in, he need to log in first
    if current_caregiver is None and current_patient is None:
        print("Please log in first!")
        return

    # Check2 : the length of the tokens has to be 2
    if len(tokens) != 2:
        print("Wrong argument number, please try again")
        return

    date = tokens[1]
    # assume input is hyphenated in the format mm-dd-yyyy
    date_tokens = date.split("-")
    month = int(date_tokens[0])
    day = int(date_tokens[1])
    year = int(date_tokens[2])

    # 这个search操作既不专属于vaccine也不专属于patient也不专属于caregiver，所以我就不把SQL语句封装在那三个类中的任何一个了
    cm = ConnectionManager()
    conn = cm.create_connection()
    cursor = conn.cursor(as_dict=True)

    get_caregiver_available = "SELECT Username FROM Availabilities WHERE Time = %s"  # %s类型即可
    try:
        d = datetime.datetime(year, month, day)
        cursor.execute(get_caregiver_available, d)
        print("The available caregivers for the selected date are:")
        for row in cursor:
            print(str(row['Username']))  # 【！！】单纯查询数据不需要commit
    except pymssql.Error:  # 这俩except只有一个会触发，因为一旦try中执行到某一步激活某个except了，就不会继续执行try中之后的语句了
        print("Error occurred when getting available Caregivers")
        return
    except ValueError:
        print("Please enter a valid date!")
        return  # 出错了的话之后的code都不要做了
    # 就算d生成失败，之前也已经create_connection了，所以这里记得要close。不过因为还要做其它SQL query，所以不在这里close

    get_vaccines_available = "SELECT Name,Doses FROM Vaccines"
    try:
        cursor.execute(get_vaccines_available)
        print("The available vaccines are:")
        for row in cursor:
            print(str(row['Name']),str(row['Doses']))
    except pymssql.Error:
        print("Error occurred when getting available vaccines")
        cm.close_connection()  # 【？？】这里做完close_connection，如果没有return，会执行到下面的close_connection吗？——会
        # 就像上面那块sql查询做完继续移步到下面——经过试验，会的
        return
    cm.close_connection()
    return



def reserve(tokens):
    # reserve <date> <vaccine>
    # check 1: check if the current logged-in user is a patient
    global current_patient
    if current_patient is None:
        print("Please login as a patient first!")
        return
    
    # check 2: the length for tokens need to be exactly 3 to include all information
    if len(tokens) != 3:
        print("Incorrect arguments number! Please try again!")
        return
    
    vName = tokens[2]
    date = tokens[1]
    caregiver_name = None
    # assume input is hyphenated in the format mm-dd-yyyy
    date_tokens = date.split("-")
    month = int(date_tokens[0])
    day = int(date_tokens[1])
    year = int(date_tokens[2])
    try:
        d = datetime.datetime(year,month,day)
    except ValueError:
        print("Please enter a valid date")
        return
    
    # check 3: the doses for the vaccine has to be at least 1
    cm = ConnectionManager()
    conn = cm.create_connection()
    cursor = conn.cursor(as_dict=True)  # 【！！】加上as_dict=True就可以用row['Doses']这种字典方式引用了

    get_vaccine_dose = "SELECT Name,Doses FROM Vaccines WHERE Name = %s"
    try:
        cursor.execute(get_vaccine_dose,vName)
        for row in cursor:
            avail_dose = row['Doses']
    except pymssql.Error:
        print("Error occurred when getting available doses")
        cm.close_connection()
        return
    
    if avail_dose < 1:
        print("Not enough doses for this vaccine! Try another one!")
        cm.close_connection
        return
    
    # step 1: randomly assigned a caregiver for the reservation on that date
    assign_caregiver = "SELECT TOP 1 * FROM Availabilities WHERE Time = %s ORDER BY NEWID()"
    try:
        cursor.execute(assign_caregiver,d)
        for row in cursor:
            caregiver_name = str(row['Username'])
    except pymssql.Error:
        print("Error occurred when getting random caregiver")
        cm.close_connection()
        return
    
    if caregiver_name is None:
        print("No available caregivers on that date! Try another date!")
        return
    
    # step 2: generate an appt and update it to the database
    # global appt_id
    patient_name = current_patient.username
    # appt_id_str = str(appt_id)  # appt_id in database is varchar
    add_appt = "INSERT INTO Appointments VALUES (%s, %s, %s, %s)"  
    # 【？？】datetime也是用%s没问题吗？caregiver的startercode是这么写的——没问题
    try:
        cursor.execute(add_appt, (str(vName),d,str(patient_name),caregiver_name))
        conn.commit()
    except pymssql.Error:  # 走到这大概率是违反key规则了
        print("Error occurred when updating Appointments!")
        cm.close_connection()
        return
    cm.close_connection
    # appt_id+=1

    # step 3: delete_availabilities
    delete_availabilities(d,caregiver_name)

    # step 4: remove doses
    remove_doses(vName,1)
    
    print("Appt made successfully!")
    return
    

# 可以把删除availabilities中tuple的操作放到某个类里，再在这里二次封装
# 也可以直接在这里都做完
# 【！！】tokens并不是一个系统关键词来表示什么参数都可以，而是我们在该命令行交互文件中定义的一个变量
def delete_availabilities(d,caregiver):
    # delete_availabilities(date,caregiver)
    # check 1: check if the current logged-in user is a patient(this function works iff a patient is making an appt )
    global current_patient
    if current_patient is None:
        print("Please login as a patient first!")  # 理论上这里不会发生这种情况，因为call该函数的reserve函数也会做这个检查
        return
    
    #  check 2: the length for tokens need to be exactly 3 to include all information (with the operation name)
    # if len(tokens) != 3:
    #     print("Incorrect arguments number! Please try again!")
    #     return
    
    caregiver_name = caregiver
    date = d  # 这里传入的date我规定应该是已经转化为datetime的类型了
    
    cm = ConnectionManager()
    conn = cm.create_connection()
    cursor = conn.cursor()

    delete_tuple = "DELETE FROM Availabilities WHERE Time = %s AND Username = %s"
    try:
        cursor.execute(delete_tuple, (date,str(caregiver_name)))
        # you must call commit() to persist your data if you don't set autocommit to True
        conn.commit()
    except ValueError:
        print("Value Error happens")  # 一般ValueError发生是在生成datetime类型时发生的，这里应该不会发生
        cm.close_connection()
        return
    except pymssql.Error:  # 【？？】上传违反key规则的tuple会触发这里吗？——本函数中会的
        print("Error occurred when removing caregiver availability")
        cm.close_connection()
        return
    cm.close_connection()
    return
    


# 风格和add_doses保持一致
def remove_doses(vName,number):  # 该方法相当于在这一层封装了vaccine类中decrease_available_doses这个方法
    #  remove_doses <vaccine> <number>
    #  check 1: check if the current logged-in user is a patient(this function works iff a patient is making an appt )
    global current_patient
    if current_patient is None:
        print("Please login as a patient first!")
        return

    #  check 2: the length for tokens need to be exactly 3 to include all information (with the operation name)
    # if len(tokens) != 3:
    #     print("Incorrect arguments number! Please try again!")
    #     return

    vaccine_name = vName
    doses = number
    vaccine = None

    if doses <= 0:
        print("number should be larger than 0!")
        return

    try:
        vaccine = Vaccine(vaccine_name, doses).get()  # 这里返回的vaccine里面doses已经变为真正的available doses了
    except pymssql.Error:
        print("Error occurred when removing doses")

    # check 3: if getter returns null, it means that this vaccine can't be removed an amount

    if vaccine is None:
            print("This vaccines doesn't exist currently, so can't be removed an amount")
    else:
        # if the vaccine is not null, meaning that the vaccine already exists in our table
        try:
            vaccine.decrease_available_doses(doses)
        except pymssql.Error:
            print("Error occurred when removing doses")
            return
    print("Doses updated!")
    return


# 此处upload_availability是当前文件中的函数
def upload_availability(tokens):  # 这里tokens是不定长不定type的，照单全收
    #  upload_availability <date>
    #  check 1: check if the current logged-in user is a caregiver
    global current_caregiver  # 这里声明global就是说用的是外部定义的current_caregiver而不是该函数内部重新定义一个current_caregiver变量
    if current_caregiver is None:
        print("Please login as a caregiver first!")
        return

    # check 2: the length for tokens need to be exactly 2 to include all information (with the operation name)
    if len(tokens) != 2:  # 第一个参数应该是命令行输入的upload_availability这个字符串
        print("Incorrect argument number! Please try again!")
        return

    date = tokens[1]  # 注意是[1]不是[0]
    # assume input is hyphenated in the format mm-dd-yyyy
    date_tokens = date.split("-")
    month = int(date_tokens[0])  # 【！！】不够robust，如果输入参数是gg或者乱七八糟的string，程序直接会崩溃
    day = int(date_tokens[1])
    year = int(date_tokens[2])
    try:
        d = datetime.datetime(year, month, day)  # datetime是三方库
        current_caregiver.upload_availability(d)  # 每个caregiver实例对应一个医生。此处upload_availability方法是caregiver的实例方法
        # print("Availability uploaded!")  # 【！！】caregiver中trycatch到error后会继续回到这层继续执行
    except ValueError:
        print("Please enter a valid date!")
    except pymssql.Error as db_err:  # 【？？】Caregiver中已经trycatch了，这边还要？——经过试验发现根本不会走到这边
        print("Error occurred when uploading availability")


def cancel(tokens):
    # 大致思路：把appt里面的tuple删除，相应vaccine的dose++（用add_doses），相应availabilities里的医生和日期INSERT进去
    # 输入参数：只有用户可以取消appt？要把所有参数都输入进来，去看看appt里有没有这样的tuple——题干要求只能传入id
    # 先调试基础部分（已完成）
    # 每次只能cancel一个appt！

    # Check 1: if someone isn't logged in, he need to log in first
    global current_patient
    global current_caregiver
    if current_caregiver is None and current_patient is None:
        print("Please log in first!")
        return

    # Check 2: the length of the tokens has to be 2
    if len(tokens) != 2:
        print("Wrong argument number, please try again")
        return

    # check 3: if there's no appt related to the user, or the appt id isn't within the appts related to the user, stop
    apptid = int(tokens[1])

    username = None
    show_appt_details = None
    if current_caregiver is not None:
        username = str(current_caregiver.username)
        show_appt_details = "SELECT * FROM Appointments WHERE cName = %s AND apptId = %d"
    if current_patient is not None:
        username = str(current_patient.username)
        show_appt_details = "SELECT * FROM Appointments WHERE pName = %s AND apptId = %d"


    cm = ConnectionManager()
    conn = cm.create_connection()
    cursor = conn.cursor(as_dict=True)

    vName = None
    date = None
    cName = None

    try:
        cursor.execute(show_appt_details,(username,apptid))
        for row in cursor:  # 经过试验证实，如果不存在这样的tuple，循环体内部甚至不会执行
            # if row is None:
            #     print("No such appt for you! Try another appt ID!")  # 即使row空的，也不会走到这里
            #     return
            # else:
            #     vName = row['vName']
            #     cName = row['cName']
            #     date = row['Time']
            #     print(vName)
            vName = row['vName']
            cName = row['cName']
            date = row['Time']
            # print("vName=",vName)
            # if vName is None:
            #     print("No such appt for you! Try another appt ID!")
            #     return
    except pymssql.Error:
        print("Error occurred when getting designated appointment")
        cm.close_connection()
        return
    if vName is None:
        print("No such appt for you! Try another appt ID!")
        return

    # delete tuples in Appointments Table
    delete_appt = "DELETE FROM Appointments WHERE apptId = %d"  # 【！！】删的时候可以只指定id，但前提是前面如果取tuple是空要return，不能往下做了！
    try:
        cursor.execute(delete_appt,apptid)
        conn.commit()
    except pymssql.Error:
        print("Error occurred when deleting tuple from Appointment Table")
        cm.close_connection()
        return
    cm.close_connection
    print("Deleting tuple from Appointment Table successfully!")  # 删除不存在的tuple是不会报错的（亲测）

    # recover doses
    try:
        vaccine = Vaccine(vName, 1).get()  # 该行使得vaccine有了类型 —— 【？？】怎么就返回None了？—— 如果vName本身是none，自然vaccine也是none
        vaccine.increase_available_doses(1)
    except pymssql.Error:
        print("Error occurred when recovering doses")
        return
    print("Doses all recovered based on the cancelled appt!")

    # recover availabilities
    cm = ConnectionManager()
    conn = cm.create_connection()
    cursor = conn.cursor(as_dict=True)

    recover_avail = "INSERT INTO Availabilities VALUES (%s, %s)"
    try:
        cursor.execute(recover_avail, (date,cName))
        # you must call commit() to persist your data if you don't set autocommit to True
        conn.commit()
    except pymssql.Error:
        print("Error occurred when recovering availability")
        cm.close_connection()
        return
    cm.close_connection()
    print("Availabilities all recovered based on the cancelled appt!")
    return


def add_doses(tokens):  # for both scenario: add new vaccines; add doses to existing vaccines
    #  add_doses <vaccine> <number>
    #  check 1: check if the current logged-in user is a caregiver
    global current_caregiver
    if current_caregiver is None:
        print("Please login as a caregiver first!")
        return

    #  check 2: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Incorrect arguments number! Please try again!")
        return

    vaccine_name = tokens[1]
    doses = int(tokens[2])
    vaccine = None

    if doses <= 0:
        print("number should be larger than 0!")
        return

    try:
        vaccine = Vaccine(vaccine_name, doses).get()  # 这里返回的vaccine里面已经有doses了
    except pymssql.Error:
        print("Error occurred when adding doses")

    # check 3: if getter returns null, it means that we need to create the vaccine and insert it into the Vaccines
    #          table

    if vaccine is None:
        try:
            vaccine = Vaccine(vaccine_name, doses)
            vaccine.save_to_db()
        except pymssql.Error:
            print("Error occurred when adding doses")
            return
    else:
        # if the vaccine is not null, meaning that the vaccine already exists in our table
        try:
            vaccine.increase_available_doses(doses)
        except pymssql.Error:
            print("Error occurred when adding doses")
            return
            # 【？？】here add return?
    print("Doses updated!")
    return


def show_appointments(tokens):
    # check 1: check if the length for the tokens is exactly 1 【？？】用户输入乱七八糟参数也允许show吗？
    if len(tokens) != 1:
        print("No arguments needed, please try again")
        return
    
    # Check 2: if someone isn't logged in, he need to log in first
    global current_patient
    global current_caregiver
    if current_caregiver is None and current_patient is None:
        print("Please log in first!")
        return

    # mark = 0 for caregivers, mark = 1 for patient
    mark = 0
    username = None
    show_appt_details = None
    if current_caregiver is not None:
        mark = 0
        username = str(current_caregiver.username)
        show_appt_details = "SELECT * FROM Appointments WHERE cName = %s"
    if current_patient is not None:
        mark = 1
        username = str(current_patient.username)
        show_appt_details = "SELECT * FROM Appointments WHERE pName = %s"  # debug半天发现是name达成nmae
    
    # print out information based on current user
    cm = ConnectionManager()
    conn = cm.create_connection()
    cursor = conn.cursor(as_dict=True)

    # 【？？】show appointments应该每个人只能看到和自己相关的比较合理吧？——比如病人只能看到和自己相关的信息，包括医生名字。但题干要求了不用输出病人自己的名字
    try:
        cursor.execute(show_appt_details,username)
        print("The appointments related to you are:")
        for row in cursor:
            if mark == 0:
                print("Appt ID:",str(row['apptId']),"Vaccine Name:",str(row['vName']),"date:",str(row['Time']),"Patient Name:",str(row['pName']))
            else:
                print("Appt ID:",str(row['apptId']),"Vaccine Name:",str(row['vName']),"date:",str(row['Time']),"Caregiver Name:",str(row['cName']))
    except pymssql.Error:
        print("Error occurred when getting appt details")
        cm.close_connection()
        return
    cm.close_connection
    return
    


def logout(tokens):
    # check 1: check if the length for the tokens is exactly 1 【？？】用户输入乱七八糟参数也允许show吗？
    if len(tokens) != 1:
        print("No arguments needed, please try again")
        return
    global current_patient
    global current_caregiver
    current_caregiver = None
    current_patient = None
    print("logout successfully")
    return



def start():
    stop = False
    while not stop:
        print()
        print(" *** Please enter one of the following commands *** ")
        print("> create_patient <username> <password>")  # //TODO: implement create_patient (Part 1)
        print("> create_caregiver <username> <password>")
        print("> login_patient <username> <password>")  #// TODO: implement login_patient (Part 1)
        print("> login_caregiver <username> <password>")
        print("> search_caregiver_schedule <date>")  #// TODO: implement search_caregiver_schedule (Part 2)
        print("> reserve <date> <vaccine>") #// TODO: implement reserve (Part 2)
        print("> upload_availability <date>")
        print("> cancel <appointment_id>") #// TODO: implement cancel (extra credit)
        print("> add_doses <vaccine> <number>")
        print("> show_appointments")  #// TODO: implement show_appointments (Part 2)
        print("> logout") #// TODO: implement logout (Part 2)
        print("> Quit")
        print()
        response = ""
        print("> Enter: ", end='')

        try:
            response = str(input())
        except ValueError:
            print("Type in a valid argument")
            break

        response = response.lower()  # 转小写,所以你输入是case insensitive的
        tokens = response.split(" ")
        if len(tokens) == 0:
            ValueError("Try Again")
            continue
        operation = tokens[0]
        if operation == "create_patient":
            create_patient(tokens)
        elif operation == "create_caregiver":
            create_caregiver(tokens)
        elif operation == "login_patient":
            login_patient(tokens)
        elif operation == "login_caregiver":
            login_caregiver(tokens)
        elif operation == "search_caregiver_schedule":
            search_caregiver_schedule(tokens)
        elif operation == "reserve":
            reserve(tokens)
        elif operation == "upload_availability":
            upload_availability(tokens)
        elif operation == cancel:
            cancel(tokens)
        elif operation == "add_doses":
            add_doses(tokens)
        elif operation == "show_appointments":
            show_appointments(tokens)
        elif operation == "logout":
            logout(tokens)
        elif operation == "quit":
            print("Thank you for using the scheduler, Goodbye!")
            stop = True
        elif operation == "cancel":
            cancel(tokens)
        else:
            print("Invalid Argument")


if __name__ == "__main__":
    # ignore the following
    '''
    // pre-define the three types of authorized vaccines
    // note: it's a poor practice to hard-code these values, but we will do this ]
    // for the simplicity of this assignment
    // and then construct a map of vaccineName -> vaccineObject
    '''

    # start command line
    print()
    print("Welcome to the COVID-19 Vaccine Reservation Scheduling Application!")

    start()
