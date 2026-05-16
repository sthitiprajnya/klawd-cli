#!/bin/bash
PYTHONPATH=. uvicorn omni_agent.api.server:app --reload --port 8000
