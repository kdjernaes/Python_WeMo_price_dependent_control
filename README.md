-------------------- Automated and price dependent On/Off-control of WeMo switches -------------------- 

Disclaimer :-):
First time coding, ever...! Only managed to succeed with help from friends, Chat GPT, genious' on github... and pure luck.

General description:
The program pulls electricity data from Energinet's API: https://www.energidataservice.dk/tso-electricity/elspotprices.
The electricity data is used to determin the X-amount of cheapest times of the current day (ex. 14:00 to 15:00 + 16:00 to 17:00) - then the WeMo switch will be On during these time-spans. 
If the current Hr-span is not on the cheapest list, the WeMo-switch will turn off and vice-versa.

*** Keep in mind that Transport and taxes are not included in the prices

Code language: Python (3.11)

Implementation:
How to run as a Windows Task Scheduler task
1. Publish (or copy?) "Main.py"
2. Run "Main.py" each hour (ex. 14:00:30) through Windows Task Scheduler. Remember to tell WTS to repeat the task each hour (indefinitely).
