import docker
import time
import requests
import json

class Framework:
    def __init__(self, image_name="controller", ports=None):
        if ports is None:
            ports = {
                '5900/tcp': 5900,
                '8501/tcp': 8501,
                '6080/tcp': 6080,
                '8080/tcp': 8080,
                '5000/tcp': 5000
            }
        self.client = docker.from_env()
        self.image_name = image_name
        self.ports = ports
        self.container = None

    def start(self):
        # Run the container in the background
        self.container = self.client.containers.run(
            self.image_name,  # Image name
            ports=self.ports,
            detach=True,  # Run in background
            tty=True  # Keep the terminal open
        )
        
        # Wait until port 5000 is accessible and returns a 200 status code
        url = "http://127.0.0.1:6080"
        print("Waiting for the container to be ready...")
        while True:
            try:
                response = requests.get(url)
                if response.status_code == 200:
                    print(f"Container started successfully with ID: {self.container.id}")
                    break  # Exit the loop once the container is ready
            except requests.exceptions.RequestException:
                # Container is not ready yet, wait and retry
                time.sleep(1)
    
    def stop(self):
        if self.container:
            self.container.stop()
            print(f"Container with ID: {self.container.id} has been stopped")
        else:
            print("No container to stop.")
    
    def __command(self, action, text=None, coordinate=None):
        url = 'http://127.0.0.1:5000/perform_action'
        headers = {
            'Content-Type': 'application/json'
        }
        data = {
            'action': action,
            'text': text,
            'coordinate': coordinate
        }

        # Send the request to the Flask API
        try:
            response = requests.post(url, headers=headers, data=json.dumps(data))
            return response
        except requests.exceptions.RequestException as e:
            print(f"Error sending command: {e}")

    def left_click(self, action="left_click", text=None, coordinate=None):
        return self.__command(action, text, coordinate)
    
    def right_click(self, action="right_click", text=None, coordinate=None):
        return self.__command(action, text, coordinate)
    
    def middle_click(self, action="middle_click", text=None, coordinate=None):
        return self.__command(action, text, coordinate)
    
    def double_click(self, action="double_click", text=None, coordinate=None):
        return self.__command(action, text, coordinate)
    
    def mouse_move(self, action="mouse_move", text=None, coordinate=None):
        return self.__command(action, text, coordinate)
    
    def mouse_move(self, action="mouse_move", text=None, coordinate=None):
        return self.__command(action, text, coordinate)
    
    def left_click_drag(self, action="left_click_drag", text=None, coordinate=None):
        return self.__command(action, text, coordinate)
    
    def cursor_position(self, action="cursor_position", text=None, coordinate=None):
        return self.__command(action, text, coordinate)
    
    def screenshot(self, action="screenshot", text=None, coordinate=None):
        return self.__command(action, text, coordinate)