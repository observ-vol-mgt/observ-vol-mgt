from pydantic import BaseModel, validator
from typing import List, Dict, Literal 

class ActionCreate(BaseModel):
    dag: str

class ActionAppend(BaseModel):
    dag: str

class ActionDelete(BaseModel):
    dag: str

class Action(BaseModel):
    action_type: Literal["create", "append", "delete"]
    create: ActionCreate = None
    append: ActionAppend = None
    delete: ActionDelete = None

class Rule(BaseModel):
    rule_id: str
    processors: List[str]
    expr: str
    duration: str
    description: str = None
    action: Action

class Rules(BaseModel):
    rules: List[Rule]

    @validator('rules')
    def rules_non_empty(cls, v):
        if not v:
            raise ValueError('Rules must not be empty')
        return v
