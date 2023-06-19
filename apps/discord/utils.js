function createCommand(name, description, func)
{
    return {name: name, description: description, execute: func};
}

function fixVoiceReceive(connection)
{
    // Play something to send a opcode 5 payload (apparently a requirement that was not documented)
    // https://github.com/discord/discord-api-docs/issues/808
    const dispatcher = connection.play("./audio/audiofix.mp3");
    dispatcher.on("error", (err) => console.log(err));
    dispatcher.on("start", () => console.log(`Guild ${connection.channel.guild.id}: Starting initial audio for payload request`));
    dispatcher.on("finish", () =>
    {
        console.log(`Guild ${connection.channel.guild.id}: Finished the initial audio`);
        dispatcher.destroy();
    });
    return dispatcher;
}

function createVoiceConnectionData(connection,
                                   VoiceRecognition,
                                   user,
                                   textChannel)
{
    return {
        connection: connection,
        textChannel: textChannel,
        voiceRecognition: VoiceRecognition,
        listeningTo: [user],
        dispatcher: undefined,
        queue: [],
        playing: undefined
        };
}

module.exports = {createCommand, fixVoiceReceive, createVoiceConnectionData};