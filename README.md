# Appointment_Schedular_System_for_COVID19_Vaccinations

A common type of application that connects to a database is a reservation system, where users schedule time slots for some centralized resource.
This application will run on the command line terminal, and connect to a database server you create with your Microsoft Azure account. We will be using Python SQL Driver pymssql to allow our Python application to connect to an Azure database. 

There are two main tasks for this application:
(1) Complete the design of the database schema with an E/R diagram and create table statements
![design](https://user-images.githubusercontent.com/58315637/173481471-30a5d610-07e4-48f1-aa0d-c4c3adad5026.jpeg)

(2) Implement the code that stores Patient information, and lets users interactively schedule their vaccine appointments.
<img width="549" alt="screenshot_Modules" src="https://user-images.githubusercontent.com/58315637/173482383-9f76bca6-64d6-49ac-9453-f3caa83fa39d.png">
for source codes, please refer to the Code Directory

-> File Architecture:
●src.main.scheduler/
  Scheduler.py: 
    ■This is the main entry point to the command-line interface application. Once you compile and run Scheduler.py, you should be able to interact with the application.
  db/:
    ■This is a folder holding all of the important components related to your database.
    ■ConnectionManager.py: This is a wrapper class for connecting to the database. Read more in 2.3.4.
  model/:
    ■This is a folder holding all the class files for your data model.
    ■You should implement all classes for your data model (e.g., patients, caregivers) in this folder. We have created implementations for Caregiver and Vaccines, and you need to complete the Patient class (which can heavily borrow from Caregiver. Feel free to define more classes or change our implementation if you want! 
●src.main.resources/
  ○create.sql: SQL create statements for your tables, we have included the create table code for our implementation. You should copy, paste, and run the code (along with all other create table statements) in your Azure Query Editor.


