@echo off
git submodule update --init
pip install requests --upgrade
pip install beautifulsoup4
pip install websocket-client --upgrade
pip install requests[security] --upgrade
echo Now copy templates/ConfigTemplate.py to ./Config.py and edit the important values there.
echo Then, run the bot using python3 main.py.
pause
