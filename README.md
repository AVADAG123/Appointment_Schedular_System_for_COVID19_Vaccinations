# Appointment_Schedular_System_for_COVID19_Vaccinations

A common type of application that connects to a database is a reservation system, where users schedule time slots for some centralized resource.<br>
This application will run on the command line terminal, and connect to a database server you create with your Microsoft Azure account. We will be using Python SQL Driver pymssql to allow our Python application to connect to an Azure database. <br><br>

There are two main tasks for this application:<br>
(1) Complete the design of the database schema with an E/R diagram and create table statements
![design](https://user-images.githubusercontent.com/58315637/173481471-30a5d610-07e4-48f1-aa0d-c4c3adad5026.jpeg)<br>

(2) Implement the code that stores Patient information, and lets users interactively schedule their vaccine appointments.
<img width="549" alt="screenshot_Modules" src="https://user-images.githubusercontent.com/58315637/173482383-9f76bca6-64d6-49ac-9453-f3caa83fa39d.png">
<br>for source codes, please refer to the Code Directory<br>
<br><br>
-> File Architecture:<br>
●src.main.scheduler/<br>
  Scheduler.py:<br> 
    ■This is the main entry point to the command-line interface application. Once you compile and run Scheduler.py, you should be able to interact with the application.<br>
  db/:<br>
    ■This is a folder holding all of the important components related to your database.<br>
    ■ConnectionManager.py: This is a wrapper class for connecting to the database.<br>
  model/:<br>
    ■This is a folder holding all the class files for your data model.<br>
    ■You should implement all classes for your data model (e.g., patients, caregivers) in this folder.<br>
●src.main.resources/<br>
  ○create.sql: SQL create statements for your tables, write the create table code for our implementation. You should copy, paste, and run the code (along with all other create table statements) in your Azure Query Editor.<br><br><br>
  
-> Setting up credentials
<br><br>
<img width="705" alt="截屏2022-06-13 下午7 51 04" src="https://user-images.githubusercontent.com/58315637/173483223-33567bf9-912e-41c6-a4e6-7985f269547b.png">
<br>
<img width="716" alt="截屏2022-06-13 下午7 51 59" src="https://user-images.githubusercontent.com/58315637/173483415-d7051e1a-4b4d-4efd-9aa4-1d68aea8c2b3.png">
<br>

<img width="712" alt="截屏2022-06-13 下午7 53 09" src="https://user-images.githubusercontent.com/58315637/173483488-34704b6c-cd1c-4d34-acdc-eab514ec5ac5.png">


