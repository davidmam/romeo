import json
import websocket
import threading
import time
from romeo import MQTTClient, load_config



class ChromiumController:
    """Control a Chromium instance via the Chrome DevTools Protocol (CDP) on port 9222."""
    
    def __init__(self, host="localhost", port=9222):
        self.host = host
        self.port = port
        self.ws_url = None
        self.ws = None
        self.message_id = 0
        self.responses = {}
        self.lock = threading.Lock()
        self._get_websocket_url()
    
    def _get_websocket_url(self):
        """Retrieve the WebSocket URL from the Chrome DevTools Protocol endpoint."""
        import urllib.request
        try:
            url = f"http://{self.host}:{self.port}/json/version"
            with urllib.request.urlopen(url, timeout=5) as response:
                data = json.loads(response.read().decode())
                self.ws_url = data.get("webSocketDebuggerUrl")
                print(f"Connected to Chromium: {data.get('Browser')}")
        except Exception as e:
            print(f"Error connecting to Chromium on port {self.port}: {e}")
            raise
    
    def connect(self):
        """Connect to the Chromium instance via WebSocket."""
        if not self.ws_url:
            raise RuntimeError("WebSocket URL not available")
        
        self.ws = websocket.WebSocketApp(
            self.ws_url,
            on_open=self._on_open,
            on_message=self._on_message,
            on_error=self._on_error,
            on_close=self._on_close
        )
        
        # Run WebSocket in a separate thread
        self.ws_thread = threading.Thread(target=self.ws.run_forever, daemon=True)
        self.ws_thread.start()
        time.sleep(1)  # Give connection time to establish
    
    def _on_open(self, ws):
        print("WebSocket connection opened")
    
    def _on_message(self, ws, message):
        """Handle incoming messages from Chromium."""
        data = json.loads(message)
        if "id" in data:
            with self.lock:
                self.responses[data["id"]] = data
    
    def _on_error(self, ws, error):
        print(f"WebSocket error: {error}")
    
    def _on_close(self, ws, close_status_code, close_msg):
        print("WebSocket connection closed")
    
    def send_command(self, method, params=None, timeout=5):
        """
        Send a command to Chromium via CDP.
        
        Args:
            method: The CDP method (e.g., "Page.navigate", "Runtime.evaluate")
            params: Dictionary of parameters for the method
            timeout: Timeout for waiting for response
        
        Returns:
            The response from Chromium
        """
        if not self.ws:
            raise RuntimeError("Not connected to Chromium")
        
        with self.lock:
            self.message_id += 1
            msg_id = self.message_id
        
        command = {
            "id": msg_id,
            "method": method,
            "params": params or {}
        }
        
        self.ws.send(json.dumps(command))
        
        # Wait for response
        start_time = time.time()
        while time.time() - start_time < timeout:
            with self.lock:
                if msg_id in self.responses:
                    return self.responses.pop(msg_id)
            time.sleep(0.1)
        
        raise TimeoutError(f"No response from Chromium for command: {method}")
    
    def navigate(self, url):
        """Navigate to a URL."""
        return self.send_command("Page.navigate", {"url": url})
    
    def evaluate(self, expression):
        """Evaluate JavaScript in the page."""
        return self.send_command("Runtime.evaluate", {"expression": expression})
    
    def take_screenshot(self):
        """Take a screenshot of the current page."""
        return self.send_command("Page.captureScreenshot")
    
    def close(self):
        """Close the connection."""
        if self.ws:
            self.ws.close()
def message_callback(client, msg):
    txt=json.loads(msg.payload.decode())
    if txt.get('juliet')==config.get('birdnetpi') and txt.get('ip'):
        client.set_remote(txt.get('ip'))
    print(txt)


# Example usage
if __name__ == "__main__":
    config=load_config(config_file='juliet.yaml')
    mqtt_client = MQTTClient(broker=config['mqtt_url'], topic=config['topic'], port=config['mqtt_port'], 
                             user=config.get('mqtt_user'), password=config.get('mqtt_password'), birdnetpi=config['birdnetpi'], onmsg=message_callback)
    mqtt_client.connect()
    
    mqtt_client.start()
    print('started')
    
    time.sleep(2)
    mqtt_client.publish(config.get('juliettopic'),f'romeo={config.get("birdnetpi")}')
    print('called romeo')
    while not mqtt_client.remote_ip:
        time.sleep(1)
        print(mqtt_client.remote_ip)

    try:
        # Create controller
        controller = ChromiumController(host="localhost", port=9222)
        controller.connect()
        
        # Navigate to a page
        print("Navigating to remote birdnet pi...")
        controller.navigate(f"http://{mqtt_client.remote_ip}")
        time.sleep(2)
        controller.close()
    except Exception as e:
        print(f"Error: {e}")
