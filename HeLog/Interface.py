from apscheduler.schedulers.background import BackgroundScheduler
import datetime
from pydb import pydb
from pyModbusTCP.client import ModbusClient
import numpy as np

class Interface():
    def __init__(self,dbname,mod_path="", host='127.0.0.1',port=503,unit_id=2,interval=20):
        self.dbname = dbname
        self.mod_path = mod_path.replace('\\','/')
        if(self.mod_path and not self.mod_path.endswith('/')): self.mod_path += '/'
        self.host = host
        self.port = port
        self.unit_id = unit_id
        
        db = pydb(dbname,mod_path,mode='w')
        db.initdb()
        
        self.registers = db.getRegisters()

        self.scheduler = BackgroundScheduler()
        self.scheduler.add_job(self.update, 'interval', seconds=interval)
        self.scheduler.start()

    def stop(self):
        self.scheduler.shutdown()

    def update(self):
        db = pydb(self.dbname,self.mod_path,mode='w')
        registerData = self.readRegisterData()
        db.insertData(registerData)
        db.closedb()

    def readRegisterData(self,registers=[]):
        client = ModbusClient(host=self.host, port=self.port, auto_open=True, unit_id=self.unit_id)

        if(registers):
            registerList = registers.copy()

        if(not registers):
            registerList = self.registers.copy()

        registers = [[registerList[0]]]

        # Split register numbers up into lists of consecutive numbers
        for i in range(1, len(registerList)):
            if registerList[i] - registerList[i - 1] == 1:
                registers[-1].append(registerList[i])
            else:
                registers.append([registerList[i]])
        
        # data = {}
        # for n,register in enumerate(registerList):
        #     data[register] = (datetime.datetime.now(),n*1.1)
        
        # return data

        # Make sure the connection is still open

        if not client.is_open:
            if not client.open():
                print("Filed to connect when reading data")

        holdingRegisters = []
        for row in registers:
            # Don't error when the client is down. just use nans
            readValues = [np.nan]*len(row)
            # readValues = [np.random.rand() for rng in range(len(row))]
            if client.is_open:
                # Read the values held in registers
                readValues = client.read_holding_registers(row[0], len(row))
            
            try:
                holdingRegisters += readValues.copy()
            except:
                holdingRegisters += [np.nan]*len(row)
                
        data = {}
        for n,register in enumerate(registerList):
            data[register] = (datetime.datetime.now(),holdingRegisters[n])

        return data
    
    def getData(self,registers,startTime,endTime,n=100):
        db = pydb(self.dbname,self.mod_path)
        results = db.getData(registers,startTime,endTime,n=100)
        db.closedb()
        return results
