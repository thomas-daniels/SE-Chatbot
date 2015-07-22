git submodule init
git submodule update
sudo apt-get update
sudo apt-get install python3-setuptools
sudo easy_install3 pip
sudo pip3 install beautifulsoup4
sudo pip3 install requests --upgrade
sudo pip3 install websocket-client --upgrade
sudo pip3 install requests[security] --upgrade
echo Now copy templates/ConfigTemplate.py to ./Config.py and edit the important values there.
echo Then, run the bot using python main.py, where python is Python 2.
echo Press any key to close the setup...
read -n 1 -s
