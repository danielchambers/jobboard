from pydantic import BaseModel, constr


class UserSaveJob(BaseModel):
    job_id: str
    platform: constr(min_length=2, max_length=50)
