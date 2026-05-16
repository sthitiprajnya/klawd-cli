#!/usr/bin/env python3
"""
R&D Continuous Daemon (Hermes-Agent Inspired)
"""
import time
import requests
import random
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - R&D Daemon - %(message)s")

API_URL = "http://localhost:8000/api/v1/jobs"

RESEARCH_TASKS = [
    "Design an architecture for an event-driven python microservice.",
    "Refactor a common sorting algorithm to use extreme multi-threading.",
    "Analyze the optimal way to structure a large scale REST API.",
    "Absorb https://github.com/psf/black and create a code formatter skill.",
]

def submit_job():
    task = random.choice(RESEARCH_TASKS)
    logging.info(f"Submitting self-evolution task: {task}")
    try:
        response = requests.post(API_URL, json={"task": task})
        if response.status_code == 200:
            logging.info(f"Job successfully queued: {response.json()['job_id']}")
    except requests.exceptions.ConnectionError:
        logging.error("Could not connect to OmniAgent API. Ensure uvicorn is running.")

def run_daemon():
    logging.info("Starting Hermes-inspired Continuous R&D Daemon...")
    while True:
        submit_job()
        sleep_time = random.randint(10, 30)
        time.sleep(sleep_time)

if __name__ == "__main__":
    run_daemon()
