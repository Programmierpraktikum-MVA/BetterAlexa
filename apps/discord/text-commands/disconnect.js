const {createCommand} = require('../utils.js');

module.exports = createCommand('disconnect',
    'disconnect from author\'s voice channel',
    async message =>
    {
        const serverInfo = message.client.voiceConnections.get(message.guild.id);

        // leave the server
        serverInfo.connection.destroy();


        // Remove from storage
        message.client.voiceConnections.delete(message.guild.id);

        console.log(`Deleted entry: Guild ${message.guild.id} from voice connections list.`)
    });