import subprocess
import requests
import os
from dotenv import load_dotenv

load_dotenv()


SERVER = os.getenv("SERVER_URI")
def recovery_database_test(url):
    print("Simulating recovery database...")
    count_messages = requests.get(url).json()
    print(f"Count of messages before restart: {count_messages['count']}")
    subprocess.run(["docker", "restart", "mongo"])
    count_messages_after_restart = requests.get(url).json()
    print(f"Count of messages after restart: {count_messages_after_restart['count']}")

recovery_database_test(SERVER + "/messages/count")