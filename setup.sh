git submodule init
git submodule update
sudo pip install beautifulsoup4
sudo pip install requests --upgrade
sudo pip install websocket-client --upgrade
sudo pip install requests[security] --upgrade
echo Now copy templates/ConfigTemplate.py to ./Config.py and edit the important values there.
echo Then, run the bot using python main.py, where python is Python 2.
echo Press any key to close the setup...
read -n 1 -s