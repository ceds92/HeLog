import sqlite3
import pandas as pd
import time
import numpy as np
from datetime import datetime

class pydb():
    def __init__(self,dbname,mod_path="",mode='r',live=False):
        self.mod_path = mod_path.replace('\\','/')
        if(self.mod_path and not self.mod_path.endswith('/')): self.mod_path += '/'

        self.dbname = mod_path + dbname
        self.db = sqlite3.connect(self.dbname)
        self.c  = self.db.cursor()

        self.mode = mode
        self.live = live

    def initdb(self):
        if(self.mode == 'r'):
            raise("Cannot write to db, mode = 'r'")
        
        self.c.execute('''
            CREATE TABLE IF NOT EXISTS registers (
                register_number INTEGER PRIMARY KEY,
                scaling_factor REAL,
                name TEXT NOT NULL,
                description TEXT
            )
        ''')

        # Create the 'data_log' table if it doesn't exist
        self.c.execute('''
            CREATE TABLE IF NOT EXISTS data_log (
                log_id INTEGER PRIMARY KEY,
                register_id INTEGER,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                value REAL,
                FOREIGN KEY (register_id) REFERENCES registers(register_id)
            )
        ''')

        if(self.live): self.db.commit()

        # Load in the registers from the csv
        df = pd.read_csv(self.mod_path + "P625-PLC-Modbus-Registers.csv", usecols=['register number', 'scaling factor', 'name', 'description'])

        # Reorder the DataFrame columns to match the SQL table structure
        # Assuming 'register number' is unique and can serve as an identifier for 'register_id'
        df = df.rename(columns={'register number': 'register_number', 'scaling factor': 'scaling_factor'})

        # Insert registers data into the database
        for _, row in df.iterrows():
            # This step avoids duplicating entries if they already exist
            self.c.execute('''
            INSERT OR IGNORE INTO registers (register_number, scaling_factor, name, description)
            VALUES (?, ?, ?, ?)
            ''', (row['register_number'], row['scaling_factor'], row['name'], row['description']))

        if(self.live): self.db.commit()

    def getRegisters(self):
        registers = [register[0] for register in self.c.execute('SELECT register_number FROM registers')]
        return registers

    def printData(self):
        print("data_log:")
        for row in self.c.execute('SELECT * FROM data_log'):
            print(row)
    
    def getDataLog(self):
        dataLog = [row for row in self.c.execute('SELECT * FROM data_log')]
        return dataLog

    def getData(self, registers, startTime, endTime, n=100):
        # First, retrieve all data points for the specified registers within the given time range.
        query = f'''
            SELECT register_id, timestamp, value FROM data_log
            WHERE register_id IN ({','.join('?' * len(registers))})
            AND timestamp BETWEEN ? AND ?
            ORDER BY timestamp ASC, register_id ASC
        '''
        self.c.execute(query, registers + [startTime, endTime])
        all_results = self.c.fetchall()

        register_results = {register: [[], []] for register in registers}  # 2D array for each register
        for result in all_results:
            register_id, timestamp_str, value = result
            if register_id in register_results:
                register_results[register_id][0].append(datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S.%f'))
                register_results[register_id][1].append(value)

        # Now, sample the results if they exceed 'n' entries
        for register in registers:
            register_results[register][1] = np.array(register_results[register][1], dtype=float)
            timestamps, values = register_results[register]
            if len(timestamps) > n:
                step = len(timestamps) // n
                sampled_timestamps = timestamps[::step]
                sampled_values     = values[::step]
                register_results[register] = [sampled_timestamps, sampled_values]

        return register_results

    def insertData(self,registerData):
        """
        registerData is a dictionary formated like:
        {<register_number> : (timestamp,value)}
        """
        if(self.mode == 'r'):
            raise("Cannot write to db, mode = 'r'")
        
        for register_number, entry in registerData.items():
            self.c.execute('''
                INSERT INTO data_log (register_id, timestamp, value)
                VALUES (?, ?, ?)
            ''', (register_number, entry[0], entry[1]))
            
        if(self.live): self.db.commit()

    def closedb(self):
        self.db.close()
