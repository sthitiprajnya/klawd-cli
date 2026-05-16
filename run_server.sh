#!/bin/bash
PYTHONPATH=. uvicorn src.presentation.api.main:app --reload --port 8000
