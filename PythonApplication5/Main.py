#!/usr/bin/env python3

import os
import datetime
import time
from xmlrpc.client import DateTime
import pywemo
import requests
import json
import pandas
import time

WeMo_IP = pywemo.setup_url_for_address("192.168.1.241") #Determines the IP and port for setup file. 
print(WeMo_IP)

WeMo_switch = pywemo.discovery.device_from_description(WeMo_IP) #Determines the actual switch (name etc.)
print(WeMo_switch)

#To see all functions within the switch, run command below:
#WeMo_switch.explain()

def turn_on(WeMo_IP): #on command: "turn_on(WeMo_IP)")
    WeMo_switch.on()

def turn_off(WeMo_IP): #off command: "turn_off(WeMo_IP)")
    WeMo_switch.off()

""" Collecting, sorting and filtering data
------------------ Electricity prices - data collected from Energinets API: https://www.energidataservice.dk/tso-electricity/elspotprices -----------------------
The API collects data for six different areas, therefore when collecting prices for ex. 24Hr, you need to collect 144 lines of data (6 areas * 24Hr) - see "Limit". 
The API contains electricity prices two days in advance (except for the weekend)

DK1 = DK West
DK2 = DK East

#144 -> one day:  
#288 -> two days
"""

Limit = 288
response = requests.get(
    url='https://api.energidataservice.dk/dataset/Elspotprices?limit={}'.format(Limit))

result = response.json() #direct data from Energinets API, .json format. 

# The following filters the data, which are applicable for today's date. The reason for doing so is that the electricity prices varies from day to day, -
# and the application choses the X-amount of cheapest hours (see "Top_X_cheapest_Hr" below) for today's date, and not mix with the next days prices. 
area_filtered_result = [record for record in result['records'] if record['PriceArea'] == 'DK1' and record['HourDK'].startswith(str(datetime.date.today()))]

""" Possibility to export collected, and filtered, data from the API.
#Exports .json to excel
dataframe = pandas.DataFrame(area_filtered_result)
output_directory = os.path.expanduser('~/Documents/test')
os.makedirs(output_directory, exist_ok=True)
excel_file = os.path.join(output_directory, 'output.xlsx')
dataframe.to_excel(excel_file, index=False)
"""

""" Possibility to print data (sorted acc. to DK1)
for record in area_filtered_result:
    print(record)
"""

#The following filters the data acc. to electricity prices (ascending).  
price_filtered_result = sorted(area_filtered_result, key=lambda x: x['SpotPriceDKK'])

""" Sorted .json list - containing data for 24Hr.
for record in price_filtered_result:
    print(record)
records = result.get('records', [])
"""

#Creating a list which only contains the X-amount of cheapest hours during the day.
#Example: if you control a de-humidifier, which much run at least 8Hr each day to maintain the humidity, then Top_X_cheapest_Hr below must be 8Hr.  
Top_X_cheapest_Hr = 4

Top_X_billigste = price_filtered_result[:Top_X_cheapest_Hr]
#print(Top_X_cheapest_Hr)

# Determining whether the time of day (ex. 14:00) is included the the X-amount of cheapest hours)---------------------------------------------------
from datetime import datetime

# Function to check if the current time (ex. 14:00) is within the given time interval
def is_within_interval(start_time, end_time):
    now = datetime.now()
    start = datetime.strptime(start_time, '%Y-%m-%dT%H:%M:%S')
    end = datetime.strptime(end_time, '%Y-%m-%dT%H:%M:%S')
    return start <= now <= end

# List of time intervals
time_intervals = Top_X_billigste

""" ...Has been used for trial and error...
time_intervals = [
    {'HourUTC': '2023-06-24T12:00:00', 'HourDK': '2023-06-24T20:00:00', 'PriceArea': 'DK1', 'SpotPriceDKK': 2.31, 'SpotPriceEUR': 0.31}
]                                          
"""

from datetime import datetime, timedelta #Used for "end_time"

if WeMo_switch:
    for interval in time_intervals:
        start_time = interval['HourDK']
        end_time = (datetime.strptime(interval['HourDK'], '%Y-%m-%dT%H:%M:%S') + timedelta(hours=1)).strftime('%Y-%m-%dT%H:%M:%S')
        if is_within_interval(start_time, end_time): #if is_within_interval(start_time, end_time):
            WeMo_switch.on()
            print("WeMo_switch turned on.")
            break
    else:
        WeMo_switch.off()
else:
    print("WeMo_switch not found")

#----------------------------------------------------------------------------------------------------------------------------------------

#Prints the X-amount of cheapest hours to turn on the switch - can be left out... 
for record in Top_X_billigste:
    print(record)
records = result.get('records', [])

from datetime import datetime

# Get the current time
current_time = datetime.now().time()

# Print the current time - can be left out
print("Current time:", current_time)

"""                                           
print('records:')
for record in records:
    print(' ', record)
"""

""" Python output with current settings:

"http://192.168.1.241:49153/setup.xml
<WeMo Insight "Affugter"> (line 13)
WeMo switch turned on. (line 16)
{'HourUTC': '2023-06-25T12:00:00', 'HourDK': '2023-06-25T14:00:00', 'PriceArea': 'DK1', 'SpotPriceDKK': -0.74, 'SpotPriceEUR': -0.1} (line 117)
{'HourUTC': '2023-06-25T11:00:00', 'HourDK': '2023-06-25T13:00:00', 'PriceArea': 'DK1', 'SpotPriceDKK': -0.74, 'SpotPriceEUR': -0.1} (line 117)
{'HourUTC': '2023-06-25T13:00:00', 'HourDK': '2023-06-25T15:00:00', 'PriceArea': 'DK1', 'SpotPriceDKK': 0.0, 'SpotPriceEUR': 0.0} (line 117)
{'HourUTC': '2023-06-25T10:00:00', 'HourDK': '2023-06-25T12:00:00', 'PriceArea': 'DK1', 'SpotPriceDKK': 0.0, 'SpotPriceEUR': 0.0} (line 117)
Current time: 12:21:58.378080" (line 127)

"""

""" How to run as a Windows Task Scheduler task
1. Publish "Main.py"
2. Run "Main.py" each hour (ex. 14:00:30) through Windows Task Scheduler. Remember to tell WTS to repeat the task each hours. 

If the current Hr-span is not on the cheapest list, the WeMo-switch will turn off and vice-versa.
Keep in mind that Transport and taxes are not included in the prices
"""