const env = require('dotenv').config({path: '../../.env'});
const {createCommand, createVoiceConnectionData} = require('../utils.js');
const {
    entersState,
    joinVoiceChannel,
    VoiceConnection,
    VoiceConnectionStatus,
    EndBehaviorType
} = require('@discordjs/voice');
const ffmpeg = require('fluent-ffmpeg');
const fs = require('fs');
const {exec} = require('child_process');

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

        let connection;
        let guildVoiceConnection = message.client.voiceConnections.get(message.guild.id)
        // Check if there is already a user being listened to
        if (guildVoiceConnection) {
            if (guildVoiceConnection.listeningTo.includes(message.author)) return message.channel.send(`Already listening to ${message.author}. To listen somewhere else, use the disconnect command first.`)
            message.channel.send(`Already listening to ${guildVoiceConnection.listeningTo[0]}. The bot will not follow you. It will however listen to you if you are in the same voice channel`)
            guildVoiceConnection.listeningTo.push(message.author);
            message.client.voiceConnections.set(guildVoiceConnection);
            return;
        } else {
            connection =
                joinVoiceChannel({
                    channelId: member.voice.channel.id,
                    guildId: message.guild.id,
                    adapterCreator: message.guild.voiceAdapterCreator
                });
            message.channel.send(`Connected to ${member.voice.channel}.`);

            message.channel.send(env.parsed.DISCORD_WARNING_MESSAGE);
        }

        try {
            await entersState(connection, VoiceConnectionStatus.Ready, 20e3);
            const receiver = connection.receiver;

            receiver.speaking.on('start', (userId) => {
                let user = message.client.users.cache.get(userId);
                if (!message.client.voiceConnections.get(message.guild.id).listeningTo.includes(user)) return;
                createListeningStream(receiver, userId, user);
            });

            message.client.voiceConnections.set(message.guild.id,
                createVoiceConnectionData(connection, undefined, member.user, message.channel));
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
            duration: 100,
        },
    });

    const oggStream = new prism.opus.OggLogicalBitstream({
        opusHead: new prism.opus.OpusHead({
            channelCount: 1,
            sampleRate: 16000,
        }),
        pageSizeControl: {
            maxPackets: 10,
        },
    });

    const filename = //'./recordings/test.ogg';
        `./recordings/${new Date().toJSON().replaceAll(":", "-")}-${getDisplayName(userId, user)}.ogg`;

    const out = createWriteStream(filename);

    console.log(`👂 Started recording ${filename}`);

    pipeline(opusStream, oggStream, out, (err) => {
            if (err) {
                console.warn(`❌ Error recording file ${filename} - ${err.message}`);
            } else {
                //
                // exec("ffmpeg -i " + filename + " " + filename.replace(".ogg", ".wav"),
                //     (error) => {
                //         if (error) {
                //             console.error('Error converting file:', error);
                //         } else {
                //             console.log('File converted successfully!');
                //         }
                //     });
                let wav_filename = filename.replace(".ogg", ".wav");
                let outStream = fs.createWriteStream(wav_filename);
                ffmpeg()
                    .input(filename)
                    .inputFormat("ogg")
                    .audioQuality(128)
                    .audioChannels(1)
                    .audioFrequency(16000)
                    .toFormat("wav")
                    .on('error', error => console.log(`Encoding Error: ${error.message}`))
                    .on('exit', () => console.log('Audio recorder exited'))
                    .on('close', () => console.log('Audio recorder closed'))
                    .on('end', () => {
                        console.log(`✅ Recorded ${filename}`);
                        console.log(`Transcoding to ${wav_filename} succeeded!`)
                        fs.unlink(filename, function (err) {
                            if (err) {
                                console.error(err);
                            } else {
                                console.log("File removed:", filename);
                            }
                        });
                    })
                    .save(outStream);

            }
        }
    );
}

function playSound(path) {

}