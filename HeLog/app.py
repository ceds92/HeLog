from bokeh.plotting import figure, curdoc
from bokeh.models import ColumnDataSource
from bokeh.layouts import column, row
from datetime import datetime
from Interface import Interface

dbname  = "live.db"
host    = '192.168.0.1'
port    = 503
unit_id = 2
interface = Interface(dbname=dbname,host=host,port=port,unit_id=unit_id,interval=5)

offset = 1
registers = {
#   "Name"   : [ID, "Description", scale factor]

    "LI524A" : [31 - offset, "Liquifier A Level LI524A", 10],            # Figure 3
    # "TE521A" : [32, "Liquifier A Cold Head Temp TE521A", 10],   # Not shown
    # "TE522A" : [33, "Liquifier A Dewar Temp TE522A", 10],       # Not shown
    "PT520A" : [34 - offset, "Liquifier A Pressure PT520A", 10],         # FIgure 3

    # "LT524B" : [35, "Liquifier B Level LT524B", 10],            # Not shown
    # "TE521B" : [36, "Liquifier B Cold Head Temp TE521B", 10],   # Not shown
    # "TE522B" : [37, "Liquifier B Dewar Temp TE522B", 10],       # Not shown
    # "PT520B" : [38, "Liquifier B Pressure PT520B", 10],         # Not shown

    # "DPT511" : [41, "HP Inlet DPT511", 10],         # Not shown

    "PT503"  : [43 - offset, "MP Storage PT503", 10],        # Figure 2
    "PT305"  : [44 - offset, "Buffer Tank PT305", 10],       # Figure 2

    "PT306"  : [45 - offset, "Inlet Pressure PT306", 10],    # Figure 1
}

registerList = [value[0] for value in registers.values()]
data = interface.getData(registers=registerList,startTime=0,endTime=datetime.now())


# Inlet Pressure Figure 1
p1 = figure(title="Inlet Pressure", x_axis_type='datetime', x_axis_label='Time', y_axis_label='Value')
registerNumber = registers["PT306"][0]
registerDesc   = registers["PT306"][1]
scaleFactor    = registers["PT306"][2]
s1_1 = ColumnDataSource(data=dict(x=data[registerNumber][0], y=data[registerNumber][1]/scaleFactor))
p1.line(x='x', y='y', source=s1_1, legend_label=registerDesc, line_width=2, line_color="blue")

# He Recovery Figure 2
p2 = figure(title="He Recovery", x_axis_type='datetime', x_axis_label='Time', y_axis_label='Value')
registerNumber = registers["PT305"][0]
registerDesc   = registers["PT305"][1]
scaleFactor    = registers["PT305"][2]
s2_1 = ColumnDataSource(data=dict(x=data[registerNumber][0], y=data[registerNumber][1]/scaleFactor))
p2.line(x='x', y='y', source=s2_1, legend_label=registerDesc, line_width=2, line_color="blue")

registerNumber = registers["PT503"][0]
registerDesc   = registers["PT503"][1]
scaleFactor    = registers["PT503"][2]
s2_2 = ColumnDataSource(data=dict(x=data[registerNumber][0], y=data[registerNumber][1]/scaleFactor))
p2.line(x='x', y='y', source=s2_2, legend_label=registerDesc, line_width=2, line_color="red")

# Liquifier A Figure 3
p3 = figure(title="Liquifiers", x_axis_type='datetime', x_axis_label='Time', y_axis_label='Value')
registerNumber = registers["PT520A"][0]
registerDesc   = registers["PT520A"][1]
scaleFactor    = registers["PT520A"][2]
s3_1 = ColumnDataSource(data=dict(x=data[registerNumber][0], y=data[registerNumber][1]/scaleFactor))
p3.line(x='x', y='y', source=s3_1, legend_label=registerDesc, line_width=2, line_color="blue")

registerNumber = registers["LI524A"][0]
registerDesc   = registers["LI524A"][1]
scaleFactor    = registers["LI524A"][2]
s3_2 = ColumnDataSource(data=dict(x=data[registerNumber][0], y=data[registerNumber][1]/scaleFactor))
p3.line(x='x', y='y', source=s3_2, legend_label=registerDesc, line_width=2, line_color="red")

def update(registers):
    registerList = [value[0] for value in registers.values()]

    data  = interface.readRegisterData(registers=registerList)
    x1_1  = data[registers["PT306"][0]][0]
    y1_1  = data[registers["PT306"][0]][1]
    sf1_1 = registers["PT306"][2]

    x2_1  = data[registers["PT305"][0]][0]
    y2_1  = data[registers["PT305"][0]][1]
    sf2_1 = registers["PT306"][2]
    x2_2  = data[registers["PT503"][0]][0]
    y2_2  = data[registers["PT503"][0]][1]
    sf2_2 = registers["PT503"][2]
    
    x3_1  = data[registers["PT520A"][0]][0]
    y3_1  = data[registers["PT520A"][0]][1]
    sf3_1 = registers["PT520A"][2]
    x3_2  = data[registers["LI524A"][0]][0]
    y3_2  = data[registers["LI524A"][0]][1]
    sf3_2 = registers["LI524A"][2]

    new_s1_1 = dict(
        x=[x1_1],
        y=[y1_1/sf1_1]
    )

    new_s2_1 = dict(
        x=[x2_1],
        y=[y2_1/sf2_1]
    )
    new_s2_2 = dict(
        x=[x2_2],
        y=[y2_2/sf2_1]
    )
    
    new_s3_1 = dict(
        x=[x3_1],
        y=[y3_1/sf3_1]
    )
    new_s3_2 = dict(
        x=[x3_2],
        y=[y3_2/sf3_2]
    )

    rollover = 10000
    s1_1.stream(new_s1_1, rollover=rollover)
    
    s2_1.stream(new_s2_1, rollover=rollover)
    s2_2.stream(new_s2_2, rollover=rollover)
    
    s3_1.stream(new_s3_1, rollover=rollover)
    s3_2.stream(new_s3_2, rollover=rollover)

# Add periodic callback to update data every 5000 milliseconds (5 seconds)
curdoc().add_periodic_callback(lambda: update(registers), 5000)

layout = row(p1, p2, p3)
curdoc().add_root(layout)
