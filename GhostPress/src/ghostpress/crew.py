from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from crewai_tools import SerperDevTool
from typing import List

from ghostpress.tools import SendEmailTool


@CrewBase
class Ghostpress():
    """
    The Syndicate Crew - 4-Agent Content Creation Pipeline
    
    Sequential Process:
    1. Insight Researcher -> Research Brief
    2. Content Architect -> Structured Outline
    3. Creative Storyteller -> Blog Post
    4. Delivery Specialist -> Email Campaign
    """

    agents: List[BaseAgent]
    tasks: List[Task]

    @agent
    def insight_researcher(self) -> Agent:
        return Agent(
            config=self.agents_config['insight_researcher'],
            tools=[SerperDevTool()], 
            verbose=True
        )

    @agent
    def content_architect(self) -> Agent:
        return Agent(
            config=self.agents_config['content_architect'],
            verbose=True
        )

    @agent
    def creative_storyteller(self) -> Agent:
        return Agent(
            config=self.agents_config['creative_storyteller'],
            verbose=True
        )

    @agent
    def delivery_specialist(self) -> Agent:
        return Agent(
            config=self.agents_config['delivery_specialist'],
            tools=[SendEmailTool()], 
            verbose=True
        )

    @task
    def research_task(self) -> Task:
        return Task(
            config=self.tasks_config['research_task'],
        )

    @task
    def outline_task(self) -> Task:
        return Task(
            config=self.tasks_config['outline_task'],
        )

    @task
    def writing_task(self) -> Task:
        return Task(
            config=self.tasks_config['writing_task'],
            output_file='output/blog_post.md'
        )

    @task
    def email_task(self) -> Task:
        return Task(
            config=self.tasks_config['email_task'],
            output_file='output/email_campaign.md' 
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
