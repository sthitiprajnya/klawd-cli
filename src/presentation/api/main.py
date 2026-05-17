import asyncio
import logging
from typing import List

from fastapi import FastAPI, BackgroundTasks, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
import uvicorn
from pydantic import BaseModel

from src.domain.agents import PlannerAgent, EngineerAgent, ReviewerAgent
from src.utils.memory import agent_memory

# Setup basic logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("WorkerLoop")

app = FastAPI()

class TaskRequest(BaseModel):
    task: str

active_connections: List[WebSocket] = []

html = """
<!DOCTYPE html>
<html>
    <head>
        <title>OmniAgent Daemon</title>
        <script>
            var ws = new WebSocket("ws://localhost:8000/ws");
            ws.onmessage = function(event) {
                var messages = document.getElementById('tasks');
                var message = document.createElement('li');
                var content = document.createTextNode(event.data);
                message.appendChild(content);
                messages.appendChild(message);
            };
        </script>
    </head>
    <body>
        <h1>OmniAgent Daemon Dashboard</h1>
        <h3>Active Background Tasks / Status Updates</h3>
        <ul id='tasks'></ul>
        <h3>Current Memory State</h3>
        <ul id='memory'></ul>
        <h3>Dynamically Registered Skills</h3>
        <ul id='skills'></ul>
    </body>
</html>
"""

@app.get("/")
async def get():
    return HTMLResponse(html)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_connections.append(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        active_connections.remove(websocket)

async def broadcast_message(message: str):
    logger.info(message)
    disconnected = []
    for connection in active_connections:
        try:
            await connection.send_text(message)
        except Exception:
            disconnected.append(connection)

    for conn in disconnected:
        if conn in active_connections:
            active_connections.remove(conn)

class OmniAgentWorker:
    def __init__(self):
        self.planner = PlannerAgent()
        self.engineer = EngineerAgent()
        self.reviewer = ReviewerAgent()
        self.max_iterations = 2  # Limit for Hermes-style self-evolution loop

    async def process_task(self, task: str):
        """Processes a single task through the entire agency lifecycle with self-evolution."""
        await broadcast_message(f"--- Starting new task: {task} ---")

        # 1. Retrieve prior context (MemPalace pattern)
        past_lessons = await asyncio.to_thread(agent_memory.retrieve_lessons, task)
        if past_lessons != "No past lessons found.":
            await broadcast_message("Applying prior lessons to this task.")

        # 2. Plan (Deerflow DAG orchestration pattern)
        plan_prompt = f"Task: {task}\nPrior Context: {past_lessons}\nCreate a structured implementation pipeline."
        plan = await asyncio.to_thread(self.planner.create_plan, plan_prompt)
        await broadcast_message(f"Pipeline Plan generated.")

        # 3. Initial Execution
        code = await asyncio.to_thread(self.engineer.write_code, plan)
        await broadcast_message(f"Initial Code generated.")

        # 4. Review & Self-Evolution Loop (Hermes pattern)
        final_review = "APPROVED"
        for i in range(self.max_iterations):
            review = await asyncio.to_thread(self.reviewer.review_code, code)
            await broadcast_message(f"Review cycle {i+1} completed.")

            # Simple check for approval vs feedback
            if "APPROVED" in review and i > 0: # Force at least one review cycle mock
                final_review = review
                break
            elif "APPROVED" in review:
                # If mock approves instantly, let's pretend it gave feedback for testing the loop
                review = "[MOCK RESPONSE] Needs optimization in loop structures."

            await broadcast_message("Feedback received. Iterating code...")
            code = await asyncio.to_thread(self.engineer.iterate_code, code, review)
            final_review = review

        # 5. Store outcome in long-term memory
        await asyncio.to_thread(agent_memory.store_outcome, task, code, final_review)
        await broadcast_message("Task completed, evolved, and memorized.\n")
        return plan, code, final_review

    async def run_worker_loop(self, task_queue: List[str]):
        """Runs the autonomous loop processing a queue of tasks."""
        await broadcast_message("Starting autonomous worker loop (GStack/Hermes/Deerflow capabilities)...")
        for task in task_queue:
            try:
                await self.process_task(task)
                await asyncio.sleep(1)
            except Exception as e:
                await broadcast_message(f"Error processing task '{task}': {e}")
        await broadcast_message("Worker loop finished processing current queue.")

worker = OmniAgentWorker()

@app.post("/task")
async def add_task(request: TaskRequest, background_tasks: BackgroundTasks):
    background_tasks.add_task(worker.process_task, request.task)
    return {"message": "Task added to background queue"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
