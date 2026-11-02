from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List
from ch4_github_slack.tools.custom_tool import MyCustomTool
from ch4_github_slack.tools.slack_tool import SlackTool
from crewai.knowledge.source.string_knowledge_source import StringKnowledgeSource

# If you want to run a snippet of code before or after the crew starts,
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators

@CrewBase
class Ch4GithubSlack():
    """Ch4GithubSlack crew"""

    agents: List[BaseAgent]
    tasks: List[Task]

    # Learn more about YAML configuration files here:
    # Agents: https://docs.crewai.com/concepts/agents#yaml-configuration-recommended
    # Tasks: https://docs.crewai.com/concepts/tasks#yaml-configuration-recommended
    
    # If you would like to add tools to your agents, you can learn more about it here:
    # https://docs.crewai.com/concepts/agents#agent-tools
    @agent
    def team_lead(self) -> Agent:
        github_tool = MyCustomTool()
        return Agent(
            config=self.agents_config['team_lead'],
            tools=[github_tool],
            verbose=True
        )

    @agent
    def project_manager(self) -> Agent:
        slack_tool = SlackTool()
        return Agent(
            config=self.agents_config['project_manager'],
            tools=[slack_tool],
            verbose=True
        )

    # To learn more about structured task outputs,
    # task dependencies, and task callbacks, check out the documentation:
    # https://docs.crewai.com/concepts/tasks#overview-of-a-task
    @task
    def retrieval_task(self) -> Task:
        return Task(
            config=self.tasks_config['retrieval_task'],
            output_file='output/issues.md'
        )
    
    @task
    def categorization_task(self) -> Task:
        return Task(
            config=self.tasks_config['categorization_task'],
            output_file='output/categorized.md'
        )
    
    @task
    def notification_task(self) -> Task:
        return Task(
            config=self.tasks_config['notification_task'],
        )

    @crew
    def crew(self) -> Crew:
        """Creates the Ch4GithubSlack crew"""
        # To learn how to add knowledge sources to your crew, check out the documentation:
        # https://docs.crewai.com/concepts/knowledge#what-is-knowledge
        #content = "This project was started in 2001 and is written in " \
        #    "PHP so while it works, there are lots of legacy patterns."
        #string_source = StringKnowledgeSource(
        #    content=content,
        #)
        return Crew(
            agents=self.agents, # Automatically created by the @agent decorator
            tasks=self.tasks, # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True,
            planning=True,
            planning_llm="anthropic/claude-sonnet-5-5",
            #knowledge_sources=[string_source], # Enable knowledge by adding the sources here. You can also add more sources to the sources list.
            # process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
        )
