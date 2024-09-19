import subprocess
import requests

def recovery_database_test(url):
    print("Simulating recovery database...")
    count_messages = requests.get(url).json()
    print(f"Count of messages before restart: {count_messages['count']}")
    subprocess.run(["docker", "restart", "mongo"])
    count_messages_after_restart = requests.get(url + "/messages/count").json()
    print(f"Count of messages after restart: {count_messages_after_restart['count']}")
import subprocess
import requests

def recovery_database_test(url):
    print("Simulating recovery database...")
    count_messages = requests.get(url).json()
    print(f"Count of messages before restart: {count_messages['count']}")
    subprocess.run(["docker", "restart", "mongo"])
    count_messages_after_restart = requests.get(url + "/messages/count").json()
    print(f"Count of messages after restart: {count_messages_after_restart['count']}")
import subprocess
import requests

def recovery_database_test(url):
    print("Simulating recovery database...")
    count_messages = requests.get(url).json()
    print(f"Count of messages before restart: {count_messages['count']}")
    subprocess.run(["docker", "restart", "mongo"])
    count_messages_after_restart = requests.get(url + "/messages/count").json()
    print(f"Count of messages after restart: {count_messages_after_restart['count']}")
