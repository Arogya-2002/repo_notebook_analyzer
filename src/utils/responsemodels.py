from pydantic import BaseModel

class PipelineStatus(BaseModel):
    task_id: str
    status: str
    report_url: str = None