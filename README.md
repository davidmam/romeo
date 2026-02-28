# romeo
Find my Birdnet Pi server

Usage:
Clone the repository to the birdnet user home directory.

Romeo is the BirdNET-Pi end. It responds to a plea (via MQTT) from Juliet.

romeo.py is installed on the BirdNET-Pi as a service. 
Install to .venv from the requirements.txt.

`python -m venv .venv`
`source .venv/bin/activate`
`pip install -r requirements.txt`

Copy romeo_default.yaml to romeo.yaml, edit the settings.
Install the service by copying romeo.service to /lib/systemd/system.
Start the service with
`sudo systemctl start romeo.service`
enable with
`sudo systemctl enable romeo.service`

Juliet is a web page that is opened up when the browser launches. It contains an mqtt client that publishes a request for the server and listens for the server response. It then navigates to the server IP.

This is currently pointed at test.mosquitto.org until wss/: is established at djcad


