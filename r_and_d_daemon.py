#!/usr/bin/env python3
"""
R&D Continuous Daemon (Hermes-Agent Inspired)
"""
import asyncio
import httpx
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

async def submit_job(client: httpx.AsyncClient):
    task = random.choice(RESEARCH_TASKS)
    logging.info(f"Submitting self-evolution task: {task}")
    try:
        response = await client.post(API_URL, json={"task": task})
        if response.status_code == 200:
            logging.info(f"Job successfully queued: {response.json()['job_id']}")
    except httpx.ConnectError:
        logging.error("Could not connect to OmniAgent API. Ensure uvicorn is running.")

async def run_daemon():
    logging.info("Starting Hermes-inspired Continuous R&D Daemon...")
    async with httpx.AsyncClient() as client:
        while True:
            await submit_job(client)
            sleep_time = random.randint(10, 30)
            await asyncio.sleep(sleep_time)

if __name__ == "__main__":
    asyncio.run(run_daemon())
