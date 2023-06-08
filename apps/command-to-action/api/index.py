from flask import Flask, request

import os
from langchain.agents import ZeroShotAgent, Tool, AgentExecutor
from langchain.memory import ConversationBufferMemory
from langchain import OpenAI, LLMChain
from langchain.utilities import GoogleSearchAPIWrapper
from langchain import LLMMathChain, SerpAPIWrapper

app = Flask(__name__)


class LangChain:
    def __init__(self):
        llm = OpenAI(temperature=0)
        llm_math_chain = LLMMathChain(llm=llm)
        # search = SerpAPIWrapper()

        tools = [
            # Tool(
            #     name="Search",
            #     func=search.run,
            #     description="useful for when you need to answer questions about current events"
            # ),
            Tool(
                name="Hello_World",
                func=self.introduction,
                description="Useful for when you're introducing yourself",
                return_direct=True
            ),
            Tool(
                name="Custom_Calculator",
                func=llm_math_chain.run,
                description="useful for when you need to answer questions about math",
                return_direct=True
            )
        ]

        prefix = """Have a conversation with a human, answering the following questions as best you can. You have access to the following tools:"""
        suffix = """Begin!"

        {chat_history}
        Question: {input}
        {agent_scratchpad}"""

        prompt = ZeroShotAgent.create_prompt(
            tools,
            prefix=prefix,
            suffix=suffix,
            input_variables=["input", "chat_history", "agent_scratchpad"]
        )
        self.memory = ConversationBufferMemory(memory_key="chat_history")
        self.llm_chain = LLMChain(llm=OpenAI(temperature=0), prompt=prompt)
        self.agent = ZeroShotAgent(llm_chain=self.llm_chain, tools=tools, verbose=True)
        self.agent_chain = AgentExecutor.from_agent_and_tools(agent=self.agent, tools=tools, verbose=True,
                                                              memory=self.memory)

    def introduction(self, name_input):
        return "Hello " + name_input + ", my name is Jarvis! How can I help you today?"


langchain = LangChain()


@app.route("/command-to-action", methods=["POST"])
def generate_cta():
    try:
        # Check if request method is POST
        if request.method != "POST":
            return "Method Not Allowed", 405

        # Parse incoming data as binary
        data = request.get_data()
        text = data.decode("utf-8")
        response = langchain.agent_chain.run(input=text)
        result = {
            "text": response,
        }

        # Respond with success message
        return {"result": result}, 200
    except Exception as e:
        print(e)
        return {"error": "Internal Server Error"}, 500


if __name__ == "__main__":
    app.run(host="::", port=3001, debug=os.environ.get("DEBUG", False))
