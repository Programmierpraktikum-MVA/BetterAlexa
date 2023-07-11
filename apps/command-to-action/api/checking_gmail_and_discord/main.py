import checking_gmail as gmail_mes
import discord_messages.checking_discord as discord_mes

def main():
    gmails = gmail_mes.retrieve_all_gmail_messages()
    discords = discord_mes.retrieve_all_discord_messages(limit=3)
    print(f"In total you have {len(gmails)+len(discords)} unread messages")
    print(f"{len(gmails)} of them are in Google inbox")
    print(f"{len(discords)} of them are in discord")
if __name__ == "__main__":
    main()