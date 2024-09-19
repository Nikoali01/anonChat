import time
import requests
from dotenv import load_dotenv
import os

load_dotenv()

SERVER = os.getenv("SERVER_URI")

def measure_response_time(url, num_requests=10000, max_allowed_time=0.1):
    times = []
    for _ in range(num_requests):
        start_time = time.time()

        response = requests.get(url)
        end_time = time.time()

        response_time = end_time - start_time
        times.append(response_time)

    print("Average time: {sum(times)/len(times)}")
    under_limit = [t for t in times if t <= max_allowed_time]
    percentage_under_limit = (len(under_limit) / num_requests) * 100

    print(f"Percentage of responses under {max_allowed_time} seconds: {percentage_under_limit}%")
    return percentage_under_limit
