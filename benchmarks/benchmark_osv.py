import time
import httpx
import sys

dependencies = [
    {"name": "django", "ecosystem": "PyPI"},
    {"name": "requests", "ecosystem": "PyPI"},
    {"name": "flask", "ecosystem": "PyPI"},
    {"name": "log4j", "ecosystem": "Maven"},
    {"name": "lodash", "ecosystem": "npm"},
    {"name": "numpy", "ecosystem": "PyPI"},
    {"name": "pandas", "ecosystem": "PyPI"},
    {"name": "pytest", "ecosystem": "PyPI"},
    {"name": "react", "ecosystem": "npm"},
    {"name": "express", "ecosystem": "npm"}
]

OSV_API = "https://api.osv.dev/v1/query"
OSV_BATCH_API = "https://api.osv.dev/v1/querybatch"

def sequential_query():
    start_time = time.time()
    for dep in dependencies:
        try:
            httpx.post(OSV_API, json={"package": {"name": dep.get("name"), "ecosystem": dep.get("ecosystem")}})
        except Exception:
            pass
    end_time = time.time()
    return end_time - start_time

def batch_query():
    start_time = time.time()
    queries = {"queries": []}
    for dep in dependencies:
        queries["queries"].append({"package": {"name": dep.get("name"), "ecosystem": dep.get("ecosystem")}})

    try:
        httpx.post(OSV_BATCH_API, json=queries)
    except Exception:
        pass

    end_time = time.time()
    return end_time - start_time

print(f"Benchmarking with {len(dependencies)} dependencies...")
seq_time = sequential_query()
batch_time = batch_query()

print(f"Sequential time: {seq_time:.4f}s")
print(f"Batch time: {batch_time:.4f}s")
print(f"Improvement: {seq_time / batch_time:.2f}x")
