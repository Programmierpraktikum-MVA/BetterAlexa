from langchain.agents import ZeroShotAgent, Tool, AgentExecutor, load_tools, initialize_agent, AgentType
from langchain.memory import ConversationBufferMemory
from langchain import OpenAI, LLMChain
from langchain.tools import StructuredTool
from spotify import SpotifyPlayer

import os

class LangChainIntegration:
    def __init__(self):
        self.spotify_auth = None

        llm = OpenAI(temperature=0)
        tools = load_tools(
            [
                #"human",
                "llm-math",
                ],
            llm=llm,
            input_func=self.get_input
        )
        spotify_tool = StructuredTool.from_function(self.spotify_player, return_direct=True)
        tools.extend([
            spotify_tool,
            Tool(
                name="introduction_without_name",
                func=self.introduction_without_name,
                description="Only to be used for when I am introducing myself without a name",
                return_direct=True
            ),
            Tool(
                name="introduction_with_name",
                func=self.introduction_with_name,
                description="Only to be used for when I am introducing myself with a name",
                return_direct=True
            ),
        ])

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
        self.agent_executor = initialize_agent(tools=tools, llm=llm, agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
                                          verbose=True)

    def introduction_without_name(self, _):
        return "Hello, my name is Jarvis! How can I help you today?"

    def introduction_with_name(self, name_input):
        return "Hello " + name_input + ", my name is Jarvis! How can I help you today?"

    def get_input(self):
        return "Test input"

    def spotify_player(self, song_title=None, artist_name=None, album_name=None, playlist_name=None):
        """Lets you specify a song, artist, album, or playlist to play on Spotify."""
        if self.spotify_auth == "undefined" or self.spotify_auth is None:
            base_url = os.environ.get("NEXT_PUBLIC_BASE_URL")
            return f"You need to authenticate with Spotify first. Go to {base_url}/spotify to do so."
        self.spotify_player = SpotifyPlayer(self.spotify_auth)
        if song_title and artist_name and song_title != "null" and artist_name != "null":
            song_info = self.spotify_player.play_song_from_artist(song_title, artist_name)
            return f"Playing  {song_info['name']}  by  {song_info['artists'][0]['name']}"
        if song_title and song_title != "null":
            song_info = self.spotify_player.play_song(song_title)
            return f"Playing  {song_info['name']}  by  {song_info['artists'][0]['name']}"
        if artist_name and artist_name != "null":
            song_info = self.spotify_player.play_artist(artist_name)
            return "Playing songs by " + artist_name
        if album_name and album_name != "null":
            song_info = self.spotify_player.play_album(album_name)
            return "Playing the album " + album_name
        if playlist_name and playlist_name != "null":
            song_info = self.spotify_player.play_playlist(playlist_name)
            return "Playing songs from the playlist " + playlist_name

