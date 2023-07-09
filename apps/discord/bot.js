const env = require('dotenv').config({path: '../../.env'});
const fs = require('fs');
const Discord = require('discord.js');
const {
    joinVoiceChannel,
    createAudioPlayer,
    createAudioResource,
    entersState,
    StreamType,
    AudioPlayerStatus,
    VoiceConnectionStatus,
    getVoiceConnection
} = require('@discordjs/voice');

// Check if token was obtained correctly.
if (env.error) throw env.error;

const client = new Discord.Client({
    intents: [
        Discord.Intents.FLAGS.GUILDS,
        Discord.Intents.FLAGS.GUILD_MESSAGES,
        Discord.Intents.FLAGS.GUILD_VOICE_STATES,
    ]
});
client.voiceConnections = new Discord.Collection();

const textCommandFiles = fs.readdirSync('./text-commands').filter(file => file.endsWith('.js'));
client.textCommands = new Discord.Collection();

client.login(env.parsed.DISCORD_TOKEN);

// add text text-commands
for (const file of textCommandFiles) {
    const command = require(`./text-commands/${file}`);
    client.textCommands.set(command.name, command)
}

client.on('ready', () => console.log('BetterAlexa Recognition Bot is Online'));

//TODO warn instead of error for deployment
client.on('error', console.error);

// Checks for text commands
client.on('messageCreate', async (message) => {
    console.log(message.content)
    if (!message.content.startsWith(env.parsed.DISCORD_PREFIX) || message.author.bot) return;

    const args = message.content.slice(env.parsed.DISCORD_PREFIX.length).trim().split(' ');
    const command = client.textCommands.get(args.shift().toLowerCase());
    if (command !== undefined) command.execute(message, args);
});

// Disconnects if user has changed channels or disconnects from the voice channel
client.on('voiceStateUpdate', (oldState, newState) => {
    if (oldState.channelID !== newState.channelID &&
        client.voiceConnections.find(info => info.listeningTo.id === newState.id)) {
        client.textCommands.get('disconnect').execute(newState);
    }
});
