''' 
[生醫訊號即時顯示系統]

從資料庫即時讀取最新資料，並繪製出波形圖
包含9個成員的生理數據，每個成員有:
h: heart rate 心率
b: breath rate 呼吸率
t: temperature 體溫
'''

import os
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5 import QtGui
import pyqtgraph as pg
import random as rd
import numpy as np
import time
from gui_RealtimeGetData_BioSig import Ui_MainWindow
import pandas as pd
from datetime import datetime, timedelta
import time
import pymysql.cursors
import configparser
class AppWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.plot_num = 9               # 總共要顯示的成員數目
        # Connect to the database
        config = configparser.ConfigParser()
        config.read('DB_Config.ini')
        self.host = config["DB_Config"]["host"]
        self.port = int(config["DB_Config"]["port"])
        self.user = config["DB_Config"]["user"]
        self.password = config["DB_Config"]["password"]
        self.db = config["DB_Config"]["db"]
        self.db_table = config["DB_Config"]["db_table"]
        self.connection = pymysql.connect(host=self.host,
        port=self.port,
        user=self.user,
        password=self.password,
        db=self.db,
        charset='utf8mb4',
        autocommit = True,
        cursorclass=pymysql.cursors.DictCursor)
        now = datetime.now()-timedelta(minutes=1)
        date_time = now.strftime("%Y-%m-%d %H:%M:%S")
        cursor = self.connection.cursor()
        sql = (
            f"SELECT * FROM {self.db}.{self.db_table} where tt > '{date_time}';"
        )
        cursor.execute(sql)
        datasets = cursor.fetchall()
        # 設定使用者資訊
        self.macid_list = [" "]
        USER_ID_NAME_df = pd.read_csv("USER_ID_NAME.csv")
        if len(list(set(pd.DataFrame(datasets))))>0:
            index_list = []
            macid_list_sort = []
            name_list = []
            macid_list = list(set(pd.DataFrame(datasets)["macid"]))
            for macid in macid_list:
                id_list = list(pd.read_csv("USER_ID_NAME.csv")["MAC#"])
                if macid in id_list:
                    index_ = id_list.index(macid)
                    index_list.append(index_)
                else:
                    print("macid："+str(macid)+" doesn't exit in USER_ID_NAME.csv")
            index_list.sort()
            for i in index_list:
                macid_list_sort.append(USER_ID_NAME_df["MAC#"][i])
                name_list.append(USER_ID_NAME_df["任務位置"][i])
            self.macid_list = macid_list_sort[:self.plot_num]
            name_list = name_list[:self.plot_num]
        if len(name_list)<self.plot_num:
            name_list.extend(["NULL"]*(self.plot_num-len(name_list)))
        self.ui = Ui_MainWindow(name_list)

        self.ui.setupUi(self)
        self.showMaximized()
        
        # self.macid_list = USER_LIST
        config = configparser.ConfigParser()
        config.read('Dot_speed.ini')
        self.dot_speed = int(config["Dot_speed"]["speed"])
        self.time_interval = 1000*self.dot_speed    # 幾毫秒更新一次圖表
        self.buffer = 30                # 繪圖的緩衝區上限 (每張圖表最多可顯示幾個點)

        # 初始化所有圖表的資料陣列
        self.initialize_data_list()

        # 初始化所有圖表相關物件
        self.setup_plot()
        
        # 開始即時更新波形圖
        self.auto_update_figure(self.time_interval)
    def setup_plot(self):
        self.padding = 0.05
        self.pen_width = 2   # 畫筆粗細

        # 設定圖表的Y軸上下界
        self.range_h_upper = 140
        self.range_h_lower = 40
        self.range_b_upper = 30
        self.range_b_lower = 10
        self.range_t_upper = 50
        self.range_t_lower = 30

        self.plot_h_list = {
            1: [self.ui.plot_h1],
            2: [self.ui.plot_h2],
            3: [self.ui.plot_h3],
            4: [self.ui.plot_h4],
            5: [self.ui.plot_h5],
            6: [self.ui.plot_h6],
            7: [self.ui.plot_h7],
            8: [self.ui.plot_h8],
            9: [self.ui.plot_h9],
            }
        
        self.plot_b_list = {
            1: [self.ui.plot_b1],
            2: [self.ui.plot_b2],
            3: [self.ui.plot_b3],
            4: [self.ui.plot_b4],
            5: [self.ui.plot_b5],
            6: [self.ui.plot_b6],
            7: [self.ui.plot_b7],
            8: [self.ui.plot_b8],
            9: [self.ui.plot_b9],
            }

        self.plot_t_list = {
            1: [self.ui.plot_t1],
            2: [self.ui.plot_t2],
            3: [self.ui.plot_t3],
            4: [self.ui.plot_t4],
            5: [self.ui.plot_t5],
            6: [self.ui.plot_t6],
            7: [self.ui.plot_t7],
            8: [self.ui.plot_t8],
            9: [self.ui.plot_t9],
            }

        self.axis_font=QtGui.QFont("Microsoft JhengHei", 10, 50)
        self.label_font=QtGui.QFont("Microsoft JhengHei", 15, 50)

        # 設定所有圖表的外觀，包括線條顏色、筆畫粗細、Y軸範圍、背景透明、顯示文字
        for i in range(1, self.plot_num+1):
            self.curve_h = self.plot_h_list[i][0].plot(y=self.h_list[i-1], pen=pg.mkPen(color="#5bb8d3", width=self.pen_width), name='heart_rate')
            self.plot_h_list[i].append(self.curve_h)
            self.label_h = pg.TextItem('', **{'color': '#5bb8d3'}, anchor=(0, 0))
            self.label_h.setPos(self.buffer-int(self.buffer*0.2), 140)
            self.label_h.setFont(self.label_font)
            self.plot_h_list[i].append(self.label_h)
            self.plot_h_list[i][0].addItem(self.label_h)
            self.plot_h_list[i][0].setYRange(self.range_h_lower, self.range_h_upper, padding=self.padding)
            self.plot_h_list[i][0].setXRange(0, self.buffer, padding=self.padding)
            self.plot_h_list[i][0].setBackground(None)
            self.plot_h_list[i][0].getAxis("bottom").setStyle(tickFont = self.axis_font)
            self.plot_h_list[i][0].getAxis("left").setStyle(tickFont = self.axis_font)

            self.curve_b = self.plot_b_list[i][0].plot(y=self.b_list[i-1], pen=pg.mkPen(color="#eef0bc", width=self.pen_width), name='breath_rate')
            self.plot_b_list[i].append(self.curve_b)
            self.label_b = pg.TextItem('', **{'color': '#eef0bc'}, anchor=(0, 0))
            self.label_b.setPos(self.buffer-int(self.buffer*0.2), 30)
            self.label_b.setFont(self.label_font)
            self.plot_b_list[i].append(self.label_b)
            self.plot_b_list[i][0].addItem(self.label_b)
            self.plot_b_list[i][0].setYRange(self.range_b_lower, self.range_b_upper, padding=self.padding)
            self.plot_b_list[i][0].setXRange(0, self.buffer, padding=self.padding)
            self.plot_b_list[i][0].setBackground(None)
            self.plot_b_list[i][0].getAxis("bottom").setStyle(tickFont = self.axis_font)
            self.plot_b_list[i][0].getAxis("left").setStyle(tickFont = self.axis_font)

            self.curve_t = self.plot_t_list[i][0].plot(y=self.t_list[i-1], pen=pg.mkPen(color="#b75121", width=self.pen_width), name='temperature')
            self.plot_t_list[i].append(self.curve_t)
            self.label_t = pg.TextItem('', **{'color': '#b75121'}, anchor=(0, 0))
            self.label_t.setPos(self.buffer-int(self.buffer*0.2), 50)
            self.label_t.setFont(self.label_font)
            self.plot_t_list[i].append(self.label_t)
            self.plot_t_list[i][0].addItem(self.label_t)
            self.plot_t_list[i][0].setYRange(self.range_t_lower, self.range_t_upper, padding=self.padding)
            self.plot_t_list[i][0].setXRange(0, self.buffer, padding=self.padding)
            self.plot_t_list[i][0].setBackground(None)
            self.plot_t_list[i][0].getAxis("bottom").setStyle(tickFont = self.axis_font)
            self.plot_t_list[i][0].getAxis("left").setStyle(tickFont = self.axis_font)

    # 初始化每張圖表的資料點列表，分為 h: heart rate, b: breath rate, t: temperature, 每個列表尺寸為 [總共幾個成員, buffer], 所有值初始化為np.nan
    def initialize_data_list(self):
        self.h_list = np.full([self.plot_num, self.buffer], np.nan)
        self.b_list = np.full([self.plot_num,self.buffer], np.nan)
        self.t_list = np.full([self.plot_num,self.buffer], np.nan)

    # 將某個一維列表向左移動(後端加入新資料、刪除第一筆)
    def left_shift(self, array, new_value):
        array[:-1] = array[1:]
        array[-1] = new_value
        return array

    '''
    此處暫時用亂數產生資料，後續需要將這段程式改為從資料庫讀取
    '''
    # 即時取得某一位成員的最新數據
    def get_data(self,macid):
        cursor = self.connection.cursor()
        sql = (
            f"SELECT * FROM {self.db}.{self.db_table} where macid='{macid}' order by tt desc limit {self.dot_speed};"
        )
        cursor.execute(sql)
        result = cursor.fetchall()
        random_h, random_b, random_t = 0, 0, 0
        for i in range(self.dot_speed):
            random_h = random_h + result[i]["hr"]
            random_b = random_b + result[i]["br"]
            random_t = random_t + result[i]["temp"]
        random_h, random_b, random_t = random_h/self.dot_speed, random_b/self.dot_speed, random_t/self.dot_speed
        return random_h, random_b, random_t


    # 自動更新所有圖表
    def auto_update_figure(self, time_interval):
        # 設定計時器，每隔 time_interval 毫秒更新一次圖
        self.timer=QTimer(self) 
        self.timer.timeout.connect(self.draw)   # 將計時器時間到達時要出發的function設定為self.draw
        self.timer.start(time_interval)         #啟動計時器，每隔固定時間會觸發一次self.draw

    
    def draw(self):
        # 對每一個成員都進行:  1.取得資料  2.繪製其心率、呼吸、體溫圖表
        index = 1
        for macid in self.macid_list:
            # 亂數產生心跳、呼吸、溫度 數值。 需要改成讀取資料庫
            if macid!=" ":
                h, b, t = self.get_data(macid)
                
                # 用前述得到數值更新所有圖表
                self.update_figure_h(h, index)
                self.update_figure_b(b, index)
                self.update_figure_t(t, index)
                index = index + 1
            else:
                print("------------------目前無接收到任何數據或是輸出儀器未開啟！------------------")
                print("------------------請確定輸出儀器已啟動後再重啟此執行程式！------------------")
    
    # 更新第index號成員的心率
    def update_figure_h(self, value1, index):
        self.plot_h_list[index][2].setText(str(int(value1)))
        self.h_list[index-1] = self.left_shift(self.h_list[index-1], value1)
        self.plot_h_list[index][1].setData(self.h_list[index-1])

    # 更新第index號成員的呼吸
    def update_figure_b(self, value1, index):
        self.plot_b_list[index][2].setText(str(int(value1)))
        self.b_list[index-1] = self.left_shift(self.b_list[index-1], value1)
        self.plot_b_list[index][1].setData(self.b_list[index-1])

    # 更新第index號成員的體溫
    def update_figure_t(self, value1, index):
        self.plot_t_list[index][2].setText(str(int(value1)))
        self.t_list[index-1] = self.left_shift(self.t_list[index-1], value1)
        self.plot_t_list[index][1].setData(self.t_list[index-1])
    

app = QApplication(sys.argv)
w = AppWindow()
w.show()

sys.exit(app.exec_())
