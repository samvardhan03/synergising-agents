from datetime import datetime, date
from typing import List, Optional, Dict, Any, Union
from enum import Enum
from pydantic import BaseModel, Field, validator
import pandas as pd

# Enums for status and types
class WorkflowStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class AgentType(str, Enum):
    FORECASTING = "forecasting"
    NEWS = "news"
    SIMULATION = "simulation"
    SUMMARY = "summary"

class DataSourceType(str, Enum):
    EXCEL = "excel"
    WORLD_BANK = "world_bank"
    FRED = "fred"
    GOOGLE_TRENDS = "google_trends"
    USDA = "usda"
    NEWS_API = "news_api"

class ForecastMetric(str, Enum):
    PRICE = "price"
    SALES = "sales"
    VOLUME = "volume"
    MARKET_SHARE = "market_share"

# Base Models
class BaseEntity(BaseModel):
    id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        use_enum_values = True
        json_encoders = {
            datetime: lambda dt: dt.isoformat()
        }

# Data Source Models
class DataSource(BaseModel):
    type: DataSourceType
    name: str
    description: Optional[str] = None
    parameters: Dict[str, Any] = Field(default_factory=dict)
    last_updated: Optional[datetime] = None

class ExcelFileInfo(BaseModel):
    filename: str
    sheet_names: List[str]
    row_count: int
    column_count: int
    columns: List[str]
    file_size: int
    upload_time: datetime = Field(default_factory=datetime.utcnow)

# Time Series Data Models
class TimeSeriesPoint(BaseModel):
    date: date
    value: float
    category: Optional[str] = None
    region: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

class TimeSeriesData(BaseModel):
    name: str
    metric: ForecastMetric
    data_points: List[TimeSeriesPoint]
    frequency: str = "daily"  # daily, weekly, monthly, quarterly, yearly
    unit: Optional[str] = None
    source: Optional[str] = None

# Forecasting Models
class ForecastRequest(BaseModel):
    time_series_data: TimeSeriesData
    forecast_horizon: int = Field(ge=1, le=365, description="Number of periods to forecast")
    confidence_level: float = Field(ge=0.5, le=0.99, default=0.95)
    model_type: str = "timegpt-1"
    include_anomaly_detection: bool = True
    external_regressors: Optional[List[TimeSeriesData]] = None

class ForecastPoint(BaseModel):
    date: date
    predicted_value: float
    lower_bound: Optional[float] = None
    upper_bound: Optional[float] = None
    confidence: float
    is_anomaly: bool = False

class ForecastResult(BaseModel):
    forecast_points: List[ForecastPoint]
    model_metrics: Dict[str, float] = Field(default_factory=dict)
    trend_analysis: Dict[str, Any] = Field(default_factory=dict)
    anomalies: List[Dict[str, Any]] = Field(default_factory=list)
    generated_at: datetime = Field(default_factory=datetime.utcnow)

# News Models
class NewsArticle(BaseModel):
    title: str
    content: str
    source: str
    published_at: datetime
    url: Optional[str] = None
    relevance_score: float = Field(ge=0.0, le=1.0)
    sentiment_score: float = Field(ge=-1.0, le=1.0)
    keywords: List[str] = Field(default_factory=list)
    category: Optional[str] = None

class NewsRequest(BaseModel):
    keywords: List[str]
    date_range: Optional[Dict[str, date]] = None
    sources: Optional[List[str]] = None
    max_articles: int = Field(ge=1, le=100, default=20)
    min_relevance: float = Field(ge=0.0, le=1.0, default=0.5)

class NewsAnalysis(BaseModel):
    articles: List[NewsArticle]
    summary: str
    key_themes: List[str]
    sentiment_overview: Dict[str, float]
    impact_assessment: str
    generated_at: datetime = Field(default_factory=datetime.utcnow)

# Simulation Models
class SimulationParameter(BaseModel):
    name: str
    current_value: float
    proposed_value: float
    change_percentage: float
    parameter_type: str  # price, promotion, inventory, etc.

class SimulationScenario(BaseModel):
    name: str
    description: str
    parameters: List[SimulationParameter]
    duration_days: int = Field(ge=1, le=365, default=30)

class SimulationRequest(BaseModel):
    base_data: TimeSeriesData
    scenarios: List[SimulationScenario]
    correlation_data: Optional[List[TimeSeriesData]] = None
    simulation_iterations: int = Field(ge=100, le=10000, default=1000)

class SimulationResult(BaseModel):
    scenario_name: str
    predicted_impact: Dict[str, float]
    confidence_intervals: Dict[str, Dict[str, float]]
    cross_category_effects: List[Dict[str, Any]] = Field(default_factory=list)
    risk_assessment: Dict[str, float]
    recommendations: List[str]

class SimulationAnalysis(BaseModel):
    scenarios: List[SimulationResult]
    best_scenario: str
    worst_scenario: str
    comparative_analysis: Dict[str, Any]
    generated_at: datetime = Field(default_factory=datetime.utcnow)

# Summary Models
class InsightPoint(BaseModel):
    title: str
    description: str
    importance: str = Field(pattern="^(high|medium|low)$")
    supporting_data: List[str] = Field(default_factory=list)
    action_items: List[str] = Field(default_factory=list)

class ExecutiveSummary(BaseModel):
    title: str
    key_findings: List[str]
    insights: List[InsightPoint]
    recommendations: List[str]
    financial_impact: Optional[Dict[str, float]] = None
    next_steps: List[str] = Field(default_factory=list)
    generated_at: datetime = Field(default_factory=datetime.utcnow)

class PresentationSlide(BaseModel):
    slide_number: int
    title: str
    content: List[str]
    chart_data: Optional[Dict[str, Any]] = None
    notes: Optional[str] = None

class Presentation(BaseModel):
    title: str
    slides: List[PresentationSlide]
    executive_summary: ExecutiveSummary
    appendix: Optional[Dict[str, Any]] = None

# Workflow Models
class WorkflowInput(BaseModel):
    data_sources: List[DataSource]
    analysis_parameters: Dict[str, Any] = Field(default_factory=dict)
    user_preferences: Dict[str, Any] = Field(default_factory=dict)

class AgentResult(BaseModel):
    agent_type: AgentType
    status: WorkflowStatus
    result: Dict[str, Any]
    execution_time: Optional[float] = None
    error_message: Optional[str] = None
    generated_at: datetime = Field(default_factory=datetime.utcnow)

class WorkflowState(BaseModel):
    workflow_id: str
    status: WorkflowStatus
    current_agent: Optional[AgentType] = None
    progress_percentage: float = Field(ge=0.0, le=100.0, default=0.0)
    agent_results: List[AgentResult] = Field(default_factory=list)
    input_data: Optional[WorkflowInput] = None
    final_result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    started_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None

# API Response Models
class APIResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    errors: Optional[List[str]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class AnalysisRequest(BaseModel):
    product_category: str = Field(min_length=1, description="Product category to analyze (e.g., 'eggs')")
    data_files: Optional[List[str]] = None
    forecast_horizon: int = Field(ge=7, le=365, default=30, description="Days to forecast")
    include_news_analysis: bool = True
    include_simulation: bool = True
    simulation_scenarios: Optional[List[str]] = None
    user_preferences: Dict[str, Any] = Field(default_factory=dict)

class AnalysisResponse(BaseModel):
    analysis_id: str
    status: WorkflowStatus
    forecasting_result: Optional[ForecastResult] = None
    news_analysis: Optional[NewsAnalysis] = None
    simulation_analysis: Optional[SimulationAnalysis] = None
    presentation: Optional[Presentation] = None
    progress: float = Field(ge=0.0, le=100.0)
    estimated_completion: Optional[datetime] = None

# WebSocket Models
class WebSocketMessage(BaseModel):
    message_type: str
    workflow_id: str
    data: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class ProgressUpdate(BaseModel):
    workflow_id: str
    agent_type: Optional[AgentType] = None
    progress_percentage: float
    status_message: str
    current_step: Optional[str] = None
