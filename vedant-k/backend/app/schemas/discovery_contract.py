from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field, ConfigDict


class RouterDecision(BaseModel):
    model_config = ConfigDict(extra="allow")

    classification: bool = False
    regression: bool = False
    clustering: bool = False
    anomaly_detection: bool = False
    time_analysis: bool = False


class DiscoveryContract(BaseModel):
    """
    Contract received from Person 1 (Data Brain).
    Person 2 consumes this contract to orchestrate statistical & ML modeling.
    """
    model_config = ConfigDict(populate_by_name=True, extra="allow")

    schema_version: str = "1.0"
    schema_definition: Dict[str, str] = Field(default_factory=dict, alias="schema")
    target_candidates: List[str] = Field(default_factory=list)
    router: RouterDecision = Field(default_factory=RouterDecision)
    quality_report: Dict[str, Any] = Field(default_factory=dict)
    fingerprint: Dict[str, Any] = Field(default_factory=dict)
    leakage_report: Dict[str, Any] = Field(default_factory=dict)
