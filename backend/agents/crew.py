"""
Crew orchestration for DataMind AI.
"""
from crewai import Crew, Process
from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq
from langchain_anthropic import ChatAnthropic
from config import settings
from agents.agents import (
    create_dataset_understanding_agent,
    create_data_cleaning_agent,
    create_eda_agent,
    create_visualization_agent,
    create_ml_engineer_agent,
    create_business_analyst_agent,
    create_report_generation_agent,
    create_qa_agent
)
from agents.tasks import (
    create_dataset_understanding_task,
    create_data_cleaning_task,
    create_eda_task,
    create_visualization_task,
    create_ml_task,
    create_business_insights_task,
    create_report_task,
    create_qa_task
)

def get_llm():
    if settings.LLM_PROVIDER == "openai" and settings.OPENAI_API_KEY:
        return ChatOpenAI(model=settings.LLM_MODEL, temperature=0.2, api_key=settings.OPENAI_API_KEY)
    elif settings.LLM_PROVIDER == "groq" and settings.GROQ_API_KEY:
        return ChatGroq(model=settings.LLM_MODEL, temperature=0.2, api_key=settings.GROQ_API_KEY)
    elif settings.LLM_PROVIDER == "anthropic" and settings.ANTHROPIC_API_KEY:
        return ChatAnthropic(model=settings.LLM_MODEL, temperature=0.2, api_key=settings.ANTHROPIC_API_KEY)
    
    # Fallback/default if API keys not set (for testing without calling real API)
    # In production, this should raise an error
    return None

class AnalysisCrew:
    def __init__(self, dataset_info: str, analysis_type: str = "full"):
        self.dataset_info = dataset_info
        self.analysis_type = analysis_type
        self.llm = get_llm()
        
        # Initialize agents
        self.understanding_agent = create_dataset_understanding_agent(self.llm)
        self.cleaning_agent = create_data_cleaning_agent(self.llm)
        self.eda_agent = create_eda_agent(self.llm)
        self.viz_agent = create_visualization_agent(self.llm)
        self.ml_agent = create_ml_engineer_agent(self.llm)
        self.business_agent = create_business_analyst_agent(self.llm)
        self.report_agent = create_report_generation_agent(self.llm)
        self.qa_agent = create_qa_agent(self.llm)

    def run_full_analysis(self, cleaning_report: str, eda_results: str, ml_results: str = "") -> str:
        """Run the complete multi-agent analysis pipeline."""
        
        # Create tasks
        task1 = create_dataset_understanding_task(self.understanding_agent, self.dataset_info)
        task2 = create_data_cleaning_task(self.cleaning_agent, self.dataset_info, cleaning_report)
        task3 = create_eda_task(self.eda_agent, self.dataset_info, eda_results)
        task4 = create_visualization_task(self.viz_agent, self.dataset_info, eda_results)
        task5 = create_ml_task(self.ml_agent, self.dataset_info, ml_results)
        
        full_analysis_context = f"Dataset:\n{self.dataset_info}\n\nEDA:\n{eda_results}\n\nML:\n{ml_results}"
        
        task6 = create_business_insights_task(self.business_agent, full_analysis_context)
        task7 = create_report_task(self.report_agent, full_analysis_context)
        task8 = create_qa_task(self.qa_agent, "Report content will be passed from previous task context internally by CrewAI if configured sequentially, but here we just pass the full context.")
        
        # For simplicity in this implementation, we run them in a sequence.
        # In a fully connected CrewAI setup, output of one task feeds into another.
        
        crew = Crew(
            agents=[
                self.understanding_agent,
                self.cleaning_agent,
                self.eda_agent,
                self.viz_agent,
                self.ml_agent,
                self.business_agent,
                self.report_agent,
                self.qa_agent
            ],
            tasks=[task1, task2, task3, task4, task5, task6, task7, task8],
            verbose=2,
            process=Process.sequential
        )
        
        result = crew.kickoff()
        return result
