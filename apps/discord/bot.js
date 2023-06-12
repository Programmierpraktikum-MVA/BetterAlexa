const env = require('dotenv').config({path: '../../.env'});
const fs = require('fs');
const Discord = require('discord.js');

// Check if token was obtained correctly.
if (env.error) throw env.error;

const textCommandFiles = fs.readdirSync('./text-commands').filter(file => file.endsWith('.js'));

const client = new Discord.Client//();
    ({
        intents: [
            Discord.Intents.FLAGS.GUILDS,
            Discord.Intents.FLAGS.GUILD_MEMBERS,
            Discord.Intents.FLAGS.GUILD_VOICE_STATES,
            Discord.Intents.FLAGS.GUILD_MESSAGES,
        ],
    })

// ({
//     intents: [
//         Discord.GatewayIntentBits.Guilds,
//         Discord.GatewayIntentBits.GuildMembers,
//         Discord.GatewayIntentBits.GuildVoiceStates,
//         Discord.GatewayIntentBits.GuildMessages,
//         Discord.GatewayIntentBits.MessageContent,
//     ],
// });

client.textCommands = new Discord.Collection();
client.voiceConnections = new Discord.Collection();

// add text text-commands
for (const file of textCommandFiles) {
    const command = require(`./text-commands/${file}`);
    client.textCommands.set(command.name, command)
}

client.once('ready', () => {
    console.log('BetterAlexa Recognition Bot is Online');
});

//TODO warn instead of error for deployment
client.on('error', (error) => console.error(error));

// Checks for text commands
client.on('message', message => {
//client.on('messageCreated', async (message) => {
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

client.login(env.parsed.DISCORD_TOKEN);