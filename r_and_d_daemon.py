#!/usr/bin/env python3
"""
R&D Continuous Daemon (Hermes-Agent Inspired)

This script continuously triggers self-evolution and R&D tasks against the
OmniAgent Enterprise API. It simulates the autonomous 24/7 self-improvement cycle.
"""
import time
import requests
import random
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - R&D Daemon - %(message)s")

API_URL = "http://localhost:8000/api/v1/jobs"

# A pool of open-ended R&D tasks designed to expand capabilities benignly
RESEARCH_TASKS = [
    "Design an architecture for an event-driven python microservice.",
    "Refactor a common sorting algorithm to use extreme multi-threading.",
    "Analyze the optimal way to structure a large scale REST API.",
    "Absorb https://github.com/psf/black and create a code formatter skill.",
    "Absorb https://github.com/pytest-dev/pytest and create a test runner skill."
]

def submit_job():
    task = random.choice(RESEARCH_TASKS)
    logging.info(f"Submitting self-evolution task: {task}")
    try:
        response = requests.post(API_URL, json={"task": task})
        if response.status_code == 200:
            logging.info(f"Job successfully queued: {response.json()['job_id']}")
        else:
            logging.warning(f"Failed to queue job. Status: {response.status_code}")
    except requests.exceptions.ConnectionError:
        logging.error("Could not connect to OmniAgent API. Ensure uvicorn is running.")

def run_daemon():
    logging.info("Starting Hermes-inspired Continuous R&D Daemon...")
    while True:
        submit_job()
        # Random sleep interval (e.g., 30s to 5 mins in prod, shortened here for example)
        sleep_time = random.randint(10, 30)
        logging.info(f"Daemon sleeping for {sleep_time} seconds before next R&D cycle.")
        time.sleep(sleep_time)

if __name__ == "__main__":
    run_daemon()
