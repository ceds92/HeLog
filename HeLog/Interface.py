from apscheduler.schedulers.background import BackgroundScheduler
import datetime
from pydb import pydb
from pyModbusTCP.client import ModbusClient
import numpy as np

class Interface():
    def __init__(self,dbname,mod_path="", host='127.0.0.1',port=503,unit_id=2,interval=20,live=False,demo=True):
        self.dbname = dbname                                                                    # Database name - saved as <dbname>.db. Using the same name as an existing db is safe and will not overwrite it
        self.mod_path = mod_path.replace('\\','/')
        if(self.mod_path and not self.mod_path.endswith('/')): self.mod_path += '/'             # Not really required for now but could come in handy later
        
        self.host = host                                                                        # Host IP of the controller
        self.port = port                                                                        # Port the controller is listening on
        self.unit_id = unit_id                                                                  # ID of the unit in the network
        self.live = live
        self.demo = demo

        db = pydb(dbname,mod_path,mode='w',live=live)                                           # Connect to the database
        db.initdb()                                                                             # Initialise the database (create tables if they don't exist)
        
        self.registers = db.getRegisters()                                                      # Get a list of all the available registers on the client (these ultimately come from the .csv)

        self.scheduler = BackgroundScheduler()                                                  # Set up a background schedular to populate the database
        self.scheduler.add_job(self.update, 'interval', seconds=interval)                       # This is the function (self.update) that runs every <interval> seconds.
        self.scheduler.start()                                                                  # Start the schedule

    def stop(self):
        """
        Calling this function stops the schedule
        """
        self.scheduler.shutdown()

    def update(self):
        """
        Update the database (if in live mode) with the latest register data.
        This function is called by the schedular every <interval> secodns.
        """
        if(not self.live): return

        registerData = self.readRegisterData()
        db = pydb(self.dbname,self.mod_path,mode='w',live=self.live)
        db.insertData(registerData)
        db.closedb()

    def readRegisterData(self,registers=[]):
        """
        This function reads the latest data held in the registers
        """
        client = None
        if(not self.demo):                                                  # Connect to the client if not in demo mode
            client = ModbusClient(host=self.host, port=self.port, auto_open=True, unit_id=self.unit_id)

        if(registers):
            registerList = registers.copy()                                 # If this function is called with a specific list of registers to read, then use this list

        if(not registers):
            registerList = self.registers.copy()                            # Otherwise we'll read all of the registers

        # Split register numbers up into lists of consecutive numbers. More efficient to read the registers like this
        registers = [[registerList[0]]]
        for i in range(1, len(registerList)):
            if registerList[i] - registerList[i - 1] == 1:
                registers[-1].append(registerList[i])
            else:
                registers.append([registerList[i]])
        
        holdingRegisters = []
        for row in registers:
            readValues = [np.nan]*len(row)                                  # Prepare a list of nan's in case the client doesn't respond for some reason

            if(self.demo):
                readValues = [np.random.rand() for rng in range(len(row))]  # Use random numbers if we're in demo mode

            if (not self.demo):
                if(not client.is_open):
                    client.open()
                    
                if(client.is_open):                                         # If we're not in demo mode, make sure the client connection is still open
                    readValues = client.read_holding_registers(row[0], len(row))# Read data from the registers
            
            try:
                holdingRegisters += readValues.copy()                       # Occassionally, the client sends back nothing so put inside try/except
            except:
                holdingRegisters += [np.nan]*len(row)                       # If the client happens to send nothing, just fill in the blanks with nan

        data = {}
        for n,register in enumerate(registerList):
            data[register] = (datetime.datetime.now(),holdingRegisters[n])  # Organise data in a dictionary where the key is the register number

        return data
    
    def getData(self,registers,startTime,endTime,n=100):
        """
        Pull the latest n records for every register in registers between
        startTime and endTime.
        """
        db = pydb(self.dbname,self.mod_path)
        results = db.getData(registers,startTime,endTime,n=100)
        db.closedb()
        return results

    def printData(self):
        db = pydb(self.dbname,self.mod_path)
        db.printData()
        db.closedb()