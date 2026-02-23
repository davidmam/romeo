# romeo
Find my Birdnet Pi server

Usage:
Clone the repository to the birdnet user home directory.

romeo.py is installed on the BirdNET-Pi as a service. copy romeo_default.yaml to romeo.yaml, edit the settings and install the service  with the appropriate scripts.
Start the service with
sudo systemctl start romeo

juliet is called on startup by the client as part of the LXDEsession initialisation. First Chromium is launched with teh remote debug port enabled. 
Juliet will then attempt to call romeo and identify the ip address for romeo. It will then call the controller to navigate to the correct IP.

#TODO
Example service scripts.
Example LXDE session startup script.