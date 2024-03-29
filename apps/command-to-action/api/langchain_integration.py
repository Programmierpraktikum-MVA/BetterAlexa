from langchain.agents import ZeroShotAgent, Tool, AgentExecutor, load_tools, initialize_agent, AgentType
from langchain.memory import ConversationBufferMemory
from langchain import LLMChain, LLMMathChain
from langchain.chat_models import ChatOpenAI
from langchain.tools import StructuredTool
from spotify import SpotifyPlayer

import os

class LangChainIntegration:
    def __init__(self):
        self.spotify_auth = None

        llm = ChatOpenAI(temperature=0)
        tools = load_tools(
            [],
            llm=llm,
        )
        spotify_tool = StructuredTool.from_function(self.spotify_player, return_direct=True)
        llm_math_chain = LLMMathChain(llm=llm)
        tools.extend([
            spotify_tool,
            Tool(
                name="Custom_Calculator",
                func=llm_math_chain.run,
                description="useful for when you need to answer questions about math",
                return_direct=False
            )
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
        self.llm_chain = LLMChain(llm=ChatOpenAI(temperature=0), prompt=prompt)
        self.agent = ZeroShotAgent(llm_chain=self.llm_chain, tools=tools, verbose=True)
        self.agent_chain = AgentExecutor.from_agent_and_tools(agent=self.agent, tools=tools, verbose=True,
                                                              memory=self.memory)
        self.agent_executor = initialize_agent(tools=tools, llm=llm, agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
                                          verbose=True)

    def spotify_player(self, song_title=None, artist_name=None, album_name=None, playlist_name=None):
        """Lets you specify a song, artist, album, or playlist to play on Spotify. The input is passed as a simple string of the song title, artist name, album name, or playlist name without json formatting."""
        if self.spotify_auth == "undefined" or self.spotify_auth is None:
            base_url = os.environ.get("NEXT_PUBLIC_BASE_URL")
            return f"You need to authenticate with Spotify first. Go to {base_url}/spotify to do so."
        try:
            self.spotify_player = SpotifyPlayer(self.spotify_auth)
        except Exception as e:
            return f"Error: {e}"
        if song_title and artist_name and song_title != "null" and artist_name != "null":
            song_info = self.spotify_player.play_song_from_artist(song_title, artist_name)
            return f"Playing {song_info['name']} by {song_info['artists'][0]['name']}"
        if song_title and song_title != "null":
            song_info = self.spotify_player.play_song(song_title)
            return f"Playing {song_info['name']} by {song_info['artists'][0]['name']}"
        if artist_name and artist_name != "null":
            song_info = self.spotify_player.play_artist(artist_name)
            return "Playing songs by " + artist_name
        if album_name and album_name != "null":
            song_info = self.spotify_player.play_album(album_name)
            return "Playing the album " + album_name
        if playlist_name and playlist_name != "null":
            song_info = self.spotify_player.play_playlist(playlist_name)
            return "Playing songs from the playlist " + playlist_name

