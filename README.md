# risinformer
RIPE RIS Informer

This project contains a few Python sripts for parsing the stream from RIPE Routing Information Service Live, detecting the BGP route leaks, hijack, updates with wrong origin, all BGP updates and withdrawals messages, and also sending serialized data to collector for vizualizing, send notifications to email, slack or telegram.
For make your config.yaml file first you should run the setup.py script and input all asked data.
After creating file prefixes.json, that contains all your objects (script also create the task in crontab for updating this file twice per day) and adding all needind data to config.yaml for sending notifications to slack and telegram you can run the main script risinformer.py.