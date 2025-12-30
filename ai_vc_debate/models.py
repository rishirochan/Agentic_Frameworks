from typing import List, Optional, Literal
from enum import Enum
from pydantic import BaseModel, Field, model_validator


# BULL CASE
class BullCase(BaseModel):
    """The optimistic investment thesis - reasons to invest."""
    startup_name: str
    one_liner: str = Field(description="What the startup does in one sentence")
    market_opportunity: str = Field(description="TAM/SAM analysis and market size")
    competitive_moat: str = Field(description="Why they'll win against competitors")
    growth_catalysts: List[str] = Field(min_length=3, description="Key growth drivers")
    traction_highlights: List[str] = Field(description="Revenue, users, partnerships, etc.")
    team_strengths: List[str] = Field(description="Why this team can execute")
    comparable_exits: List[str] = Field(description="Similar successful acquisitions/IPOs")
    confidence_score: int = Field(ge=1, le=10, description="1-10 investment confidence")
    investment_thesis_summary: str = Field(description="The bull case in 2-3 sentences")


# BEAR CASE
class BearCase(BaseModel):
    """The skeptical risk analysis - reasons NOT to invest."""
    startup_name: str
    market_risks: List[str] = Field(min_length=2, description="Market saturation, timing, size risks")
    execution_risks: List[str] = Field(min_length=2, description="Team, ops, scaling challenges")
    competitive_threats: List[str] = Field(description="Who could kill this company")
    financial_concerns: List[str] = Field(description="Burn rate, unit economics, funding risks")
    regulatory_risks: Optional[List[str]] = Field(default=None, description="Legal/compliance issues")
    technology_risks: Optional[List[str]] = Field(default=None, description="Tech debt, obsolescence")
    key_weaknesses: List[str] = Field(min_length=3, description="Top 3+ critical weaknesses")
    kill_scenario: str = Field(description="The most likely way this startup fails")
    risk_severity_score: int = Field(ge=1, le=10, description="1-10 overall risk level")


# FINAL DECISION 
class InvestmentDecision(str, Enum):
    INVEST = "INVEST"
    PASS = "PASS"
    FOLLOW_UP = "FOLLOW_UP"


class RiskMitigation(BaseModel):
    """A single risk and its mitigation strategy."""
    risk: str
    mitigation: str


class FinalDecision(BaseModel):
    """Investment Committee verdict. GUARDRAIL: Cannot INVEST with unresolved risks."""
    startup_name: str
    decision: InvestmentDecision
    investment_thesis: str = Field(description="The synthesized reasoning for the decision")
    
    unresolved_risks: List[str] = Field(
        default_factory=list,
        description="Risks from BearCase that remain unmitigated. MUST be empty for INVEST decision."
    )
    
    risk_mitigations: List[RiskMitigation] = Field(
        default_factory=list,
        description="List of risks and how they are mitigated"
    )
    
    bull_case_weight: int = Field(ge=0, le=100, description="How much weight given to bull case (0-100%)")
    bear_case_weight: int = Field(ge=0, le=100, description="How much weight given to bear case (0-100%)")
    recommended_check_size: Optional[str] = Field(default=None, description="e.g., '$500K seed check'")
    key_due_diligence: Optional[List[str]] = Field(default=None, description="What to verify before writing check")
    follow_up_questions: Optional[List[str]] = Field(default=None, description="Questions for founders")

    @model_validator(mode='after')
    def invest_requires_addressed_risks(self) -> 'FinalDecision':
        """Blocks INVEST if unresolved_risks is not empty."""
        if self.decision == InvestmentDecision.INVEST and len(self.unresolved_risks) > 0:
            raise ValueError(
                f"INVESTMENT BLOCKED: Cannot recommend INVEST with {len(self.unresolved_risks)} unresolved risks: "
                f"{self.unresolved_risks}. "
                f"Either address these risks in 'risk_mitigations' or change decision to PASS/FOLLOW_UP."
            )
        
        if self.bull_case_weight + self.bear_case_weight != 100:
            raise ValueError(
                f"Bull case weight ({self.bull_case_weight}%) + Bear case weight ({self.bear_case_weight}%) "
                f"must equal 100%"
            )
        
        return self
