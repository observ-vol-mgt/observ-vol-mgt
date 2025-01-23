from pydantic import BaseModel, validator
from typing import List, Literal, Union
from models.ProcessorsConfig import *

class ActionCreateDAG(BaseModel):
    action_type: Literal["create_dag"]
    processors: List[Processor]
    dag: List[DAGNode] = None

class ActionDeleteDAG(BaseModel):
    action_type: Literal["delete_dag"]

#class Action(BaseModel):
#    action_type: Literal["create_dag", "delete_dag", "insert_node", "append_node", "delete_node"]
#    create_dag: ActionCreate = None
#    delete_dag: ActionAppend = None

class Rule(BaseModel):
    rule_id: str
    processors: List[str]
    expr: str
    duration: str
    description: str = None
    firing_action: Union[ActionCreateDAG, ActionDeleteDAG]
    resolved_action: Union[ActionDeleteDAG, ActionDeleteDAG]

class Rules(BaseModel):
    rules: List[Rule]

    @validator('rules')
    def rules_non_empty(cls, v):
        if not v:
            raise ValueError('Rules must not be empty')
        return v
