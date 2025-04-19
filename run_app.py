"""
Run app.

Use host 127.0.0.1 to run the app locally. This is useful for testing during 
development.

You can also run the app from your machine and expose it to other devices 
within your private network. This may be useful for testing before 'production' 
deployment.

To do this, find the private IP assigned to your device in whichever private 
network you're using and store it as an environment variable named 'SERVER_IP'. 
The app will be served from this device on port 8000. For example, I used the 
private IP assigned to my laptop in my home network.

NOTE: You may need to create an inbound firewall rule to allow incoming network 
traffic from local devices (on your private network) to the specified port on your 
machine.
"""

import os

import uvicorn


if __name__ == "__main__":
    
    uvicorn.run(
        "src.app:app", 
        host=os.getenv("SERVER_IP", "127.0.0.1"), 
        port=os.getenv("SERVER_PORT", 8000), 
        reload=False,
        log_config=None
    )
