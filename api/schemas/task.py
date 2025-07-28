from pydantic import BaseModel, Field
import datetime

class TaskBase(BaseModel):
    title: str | None = Field(None, example="세탁소에 맡긴 것을 찾으러 가기")
    due_date: datetime.date | None = Field(None, example="2025-07-21")

class TaskCreate(TaskBase):
    # title: str | None = Field(None, example="세탁소에 맡긴 것을 찾으러 가기")
    pass

class Task(TaskBase):
    id: int
    #title: str | None = Field(None, example="세탁소에 맡긴 것을 찾으러 가기")
    done: bool = Field(False, description="완료 플래그")

    class Config:
        orm_mode=True

class TaskCreateResponse(TaskCreate):
    id: int

    class Config:
        orm_mode=True