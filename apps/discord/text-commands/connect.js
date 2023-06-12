const env = require('dotenv').config({path: '../../.env'});
const {createCommand, fixVoiceReceive, createVoiceConnectionData} = require('../utils.js');
const {entersState, joinVoiceChannel, VoiceConnection, VoiceConnectionStatus, EndBehaviorType} = require('@discordjs/voice');

if (env.error) throw env.error;

module.exports = createCommand("connect",
    "connect to server and set up streams.",
    async message => {
        /*
        * Check if bot has all the permissions it needs to execute the command.
        */
        const member = message.member;
        const botPermissions = message.channel.permissionsFor(message.client.user);

        // Check if bot has permission to message in channel.
        if (!botPermissions.has("SEND_MESSAGES")) {
            // Message user for sending message access in respective text channel
            return message.channel.send(`I do not have permissions to message in the text channel ${message.channel}. Give me permission or use the command in a different text channel.`);
        }

        // Check if there is already a user being listened to (to avoid multiple streams that may break things)
        if (message.client.voiceConnections.get(message.guild.id)) {
            return mess8age.channel.send(`Already listening to <@${message.client.voiceConnections.get(message.guild.id).listeningTo.id}>`)
        }

        // User who made the command is not in a voice channel
        if (!member.voice.channel) return message.channel.send(`<@${message.author.id}> is not connected to a voice channel.`);

        const voiceChannelPermissions = member.voice.channel.permissionsFor(message.client.user);

        // Check if bot has permissions to speak and connection in the user's voice channel
        if (!voiceChannelPermissions.has("SPEAK") || !voiceChannelPermissions.has("CONNECT")) {
            return message.channel.send(`Can not connect to<@${message.author.id}>'s voice channel.
            I need speak and connect permissions to the voice channel.`);
        }


        /*
        * Create voice connection and set up streams.
         */
        const connection =
            joinVoiceChannel({
                channelId: member.voice.channel.id,
                guildId: message.guild.id,
                adapterCreator: message.guild.voiceAdapterCreator
            });
        message.channel.send(`Connected to ${member.voice.channel}.`);

        message.channel.send(env.parsed.DISCORD_WARNING_MESSAGE);

        try {
            await entersState(connection, VoiceConnectionStatus.Ready, 20e3);
            const receiver = connection.receiver;

            receiver.speaking.on('start', (userId) => {
                createListeningStream(receiver, userId, message.client.user);
            });
        } catch (error) {
            console.warn(error);
            message.channel.send('Failed to join voice channel within 20 seconds, please try again later!');
        }
    });

function getDisplayName(userId, user) {
    return user ? `${user.username}_${user.discriminator}` : userId;
}

function createListeningStream(receiver, userId, user) {
    const {createWriteStream} = require('fs');
    const {pipeline} = require('stream');
    const prism = require('prism-media');

    const opusStream = receiver.subscribe(userId, {
        end: {
            behavior: EndBehaviorType.AfterSilence,
            duration: 1000,
        },
    });

    const oggStream = new prism.opus.OggLogicalBitstream({
        opusHead: new prism.opus.OpusHead({
            channelCount: 2,
            sampleRate: 48000,
        }),
        pageSizeControl: {
            maxPackets: 10,
        },
        crc: false
    });

    const filename = `./recordings/${Date.now()}-${getDisplayName(userId, user)}.ogg`;

    const out = createWriteStream(filename);

    console.log(`👂 Started recording ${filename}`);

    pipeline(opusStream, oggStream, out, (err) => {
        if (err) {
            console.warn(`❌ Error recording file ${filename} - ${err.message}`);
        } else {
            console.log(`✅ Recorded ${filename}`);
        }
    });
}