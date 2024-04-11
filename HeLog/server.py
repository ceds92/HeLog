import plotly.express as px
import pandas as pd
from flask import Flask, request, jsonify
from App import App

app = Flask(__name__)
logger = App(dbname="mydatabase.db",host='192.168.0.1')

@app.route('/stop')
def stop():
    logger.stop()
    print("stopped!")
    return {"status": "Stopped!"}, 200

@app.route('/data', methods=['GET'])
def get_data():
    start = request.args.get('start')
    end = request.args.get('end')
    # data = fetch_data(start, end)
    data = logger.getDataLog()
    return jsonify(data)

# Dummy function to illustrate data fetching
def fetch_data(start, end):
    # This should interact with your database to fetch data between the start and end times
    return pd.DataFrame({
        'timestamp': pd.date_range(start, end, freq='5S'),
        'value': [1, 2, 3]  # Replace with actual fetched data
    })

if __name__ == '__main__':
    app.run(debug=False)
    
# In your Dash app, you would fetch from '/data' and plot using:
# df = fetch_data('2023-01-01', '2023-01-02')  # Example dates
# fig = px.line(df, x='timestamp', y='value')
# fig.show()
