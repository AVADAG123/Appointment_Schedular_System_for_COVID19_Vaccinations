CREATE TABLE Caregivers (
    Username varchar(255),
    Salt BINARY(16),
    Hash BINARY(16),
    PRIMARY KEY (Username)
);

CREATE TABLE Patients (
    Username varchar(255),
    Salt BINARY(16),
    Hash BINARY(16),
    PRIMARY KEY (Username)
);

CREATE TABLE Availabilities (
    Time date,
    Username varchar(255) REFERENCES Caregivers,
    PRIMARY KEY (Time, Username)
);

CREATE TABLE Vaccines (
    Name varchar(255),
    Doses int,
    PRIMARY KEY (Name)
);

CREATE TABLE Appointments (
    apptId int IDENTITY(1,1) PRIMARY KEY,  -- appointment id, auto-increment
    vName varchar(255),  -- vaccines name
    Time date,
    pName varchar(255),  -- patient name
    cName varchar(255),  -- caregiver name
    FOREIGN KEY(vName) REFERENCES Vaccines(Name),  -- 确定foreign key任意2个无法限制第三个
    FOREIGN KEY(pName) REFERENCES Patients(Username),
    FOREIGN KEY(cName) REFERENCES Caregivers(Username),  -- typical Multiway Relations (can refer to related ppt)
);