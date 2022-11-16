# Biomedical-signal-real-time-display-system
Biomedical signals are displayed in real time, and sensors of body temperature, respiration and heartbeat are output to the database. This database is built using MySQL Server, and its data is read from the database and then displayed on the display interface.
# DataBase
Use mysql server as DataBase. pymysql for using the connection package.

macid : Sensor ID

tt : Datetime

hr : heartbeat

br : respiration

temp : body temperature

<img width="30%" src="https://github.com/fredericklee602/Biomedical-signal-real-time-display-system/blob/main/image/SQL_Table.PNG?raw=true" alt="Home Page">

# Setting
#### DB_Config.ini
SQL setting : host, port, user, password, db, db_table

#### USER_ID_NAME.csv
Before starting the execution, you must fill in the corresponding roles and sensor labels in this csv file.

<img width="30%" src="https://github.com/fredericklee602/Biomedical-signal-real-time-display-system/blob/main/image/id_name_pair.PNG?raw=true" alt="Home Page">

#### Dot_speed.ini
Set N seconds, the data of this N seconds is averaged and then output.

# Execute
Install the required packages
```Shell
pip install -r requirements.txt
```
Run the main program

```Shell
python main_RealtimeGetData_BioSig.py
```

## Execution screen

First, select data from DataBase, then sort the characters according to USER_ID_NAME.csv, and then display their data in sequence.

<img width="50%" src="https://github.com/fredericklee602/Biomedical-signal-real-time-display-system/blob/main/image/Bio_interface.PNG?raw=true" alt="Home Page">
