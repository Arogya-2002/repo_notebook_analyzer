import os
import shutil
import uuid
from typing import Dict
from fastapi import FastAPI, UploadFile, File, BackgroundTasks, HTTPException
from fastapi.responses import FileResponse

from src.logger import logging
from main import initiate_report_generator_pipeline

from src.constants import MAX_FILE_SIZE_MB,MAX_FILE_SIZE_BYTES
from src.utils.responsemodels import PipelineStatus

app = FastAPI(title="Student Repo Analyzer API", version="1.0.0")

tasks_status: Dict[str, Dict] = {}

def run_pipeline_task(task_id: str, file_path: str):
    """Worker function to run the pipeline in the background."""
    try:
        tasks_status[task_id]["status"] = "Processing"
        logging.info(f"Background Task {task_id} started for file: {file_path}")
        
        # Execute the core pipeline logic
        report_path = initiate_report_generator_pipeline(file_path)
        
        tasks_status[task_id]["status"] = "Completed"
        tasks_status[task_id]["report_path"] = report_path
        logging.info(f"Background Task {task_id} finished successfully.")
    except Exception as e:
        tasks_status[task_id]["status"] = f"Failed"
        tasks_status[task_id]["error"] = str(e)
        logging.error(f"Background Task {task_id} failed: {e}")

@app.post("/analyze", response_model=PipelineStatus)
async def analyze_students(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    """
    Uploads an Excel file with size validation and starts background processing.
    """
    # 1. Validate File Extension
    if not file.filename.lower().endswith(('.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail="Invalid file format. Please upload an Excel file.")

    # 2. Validate File Size
    # We read the file size without loading the entire file into memory immediately
    try:
        file.file.seek(0, os.SEEK_END)
        file_size = file.file.tell()
        file.file.seek(0)  # Reset cursor to beginning of file

        if file_size > MAX_FILE_SIZE_BYTES:
            logging.warning(f"File upload rejected: {file.filename} is {file_size/(1024*1024):.2f}MB")
            raise HTTPException(
                status_code=413, 
                detail=f"File too large. Maximum allowed size is {MAX_FILE_SIZE_MB}MB."
            )
    except Exception as e:
        if isinstance(e, HTTPException): raise e
        raise HTTPException(status_code=500, detail=f"Error checking file size: {str(e)}")

    # 3. Setup Task and Save File
    task_id = str(uuid.uuid4())
    upload_dir = "uploads"
    os.makedirs(upload_dir, exist_ok=True)
    
    file_path = os.path.join(upload_dir, f"{task_id}_{file.filename}")
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    tasks_status[task_id] = {"status": "Queued", "report_path": None}
    
    # 4. Trigger Pipeline in Background
    background_tasks.add_task(run_pipeline_task, task_id, file_path)

    return {
        "task_id": task_id,
        "status": "Queued",
        "report_url": f"/status/{task_id}"
    }

@app.get("/status/{task_id}")
async def get_status(task_id: str):
    if task_id not in tasks_status:
        raise HTTPException(status_code=404, detail="Task ID not found")
    return tasks_status[task_id]

@app.get("/download/{task_id}")
async def download_report(task_id: str):
    task = tasks_status.get(task_id)
    if not task or task["status"] != "Completed":
        raise HTTPException(status_code=400, detail="Report not ready or task failed")
    
    return FileResponse(
        path=task["report_path"], 
        filename=os.path.basename(task["report_path"]),
        media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)