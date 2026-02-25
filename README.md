# romeo
Find my Birdnet Pi server

Usage:
Clone the repository to the birdnet user home directory.

Romeo is the BirdNET-Pi end. It responds to a plea (via MQTT) from Juliet.

romeo.py is installed on the BirdNET-Pi as a service. 
Install to .venv from the requirements.txt.
pip install -r requirements.txt

Copy romeo_default.yaml to romeo.yaml, edit the settings.
Install the service by copying romeo.service to /lib/systemd/system.
Start the service with
sudo systemctl start romeo.service
enable with
sudo systemctl enable romeo.service

Juliet is a script run on the client. It seeks romeo and then points a chromium browser (via the rremote debug port on 9222) to the romeo IP.

Juliet is called on startup by the client as part of the LXDEsession initialisation. First Chromium is launched with teh remote debug port enabled. 
Juliet will then attempt to call romeo and identify the ip address for romeo. It will then call the controller to navigate to the correct IP.

#TODO
Example service scripts.
Example LXDE session startup script.