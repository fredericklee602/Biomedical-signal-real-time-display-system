import pymysql.cursors
# Connect to the database
connection = pymysql.connect(host='192.168.1.32',
port=3306,
user='ecgdemo',
password='demodemo',
db='ecgdemo',
charset='ecglog',
cursorclass=pymysql.cursors.DictCursor)
import pandas as pd
df = pd.read_csv("demo.csv")
import time
from datetime import datetime
import random as rd
cursor = connection.cursor()
range_h_upper = 140
range_h_lower = 40
range_b_upper = 30
range_b_lower = 10
range_t_upper = 50
range_t_lower = 30
import pandas as pd
list_ = pd.read_csv("USER_ID_NAME.csv")["MAC#"].tolist()
for i, raw in df.iterrows():
    time.sleep(1)
    for macid in list_:
        now = datetime.now()
        date_time = now.strftime("%Y-%m-%d %H:%M:%S")
        hr = rd.gauss((range_h_lower+range_h_upper)/2, 1)
        br = rd.gauss((range_b_lower+range_b_upper)/2, 1)
        temp = rd.gauss((range_t_lower+range_t_upper)/2, 1)
        local = raw["local"]
        sql = f'INSERT INTO `test`.`test` (`macid`, `tt`, `hr`, `br`, `temp`, `local`) VALUES (\'{macid}\', \'{date_time}\', {hr}, {br}, {temp}, \'{local}\')'
        cursor.execute(sql)
        print(date_time)
        connection.commit()