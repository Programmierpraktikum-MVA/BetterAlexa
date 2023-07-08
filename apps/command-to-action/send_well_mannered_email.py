from email.message import EmailMessage
import ssl
import smtplib
import openai

#trying to pull contacts  #failed try
#import atom
#import gdata.contacts       #pip install gdata
#import gdata.contacts.service


global email_sender 
global email_passwort 
email_sender = 'dummybetteralexa@gmail.com'    #to access my google account and gmail directly in browser use passwort: betterAlexaDummy!23
email_passwort = 'gphradmrreneocck'            #it is an app-passwort => to access gmail working here in the code 

global full_name_of_sender
full_name_of_sender = "Dummy BeterAlexa"

def generate_email(target, given_prompt):
    openai.api_key = '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'  # Replace with your OpenAI API key

    prompt_to_chatGPT= f"Act as my assistant. Write {full_name_of_sender} in the end instead of Your name. Write a short and well-mannered email to {target} about:\n {given_prompt}"
    
    response = openai.Completion.create(
        engine='text-davinci-003',
        prompt=prompt_to_chatGPT,
        max_tokens=1024,
        temperature=0.5,
        n=1,
        stop=None
    )

    return response.choices[0].text.strip()

def generate_subject_for_email(email_prompt):
    openai.api_key = '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'  # Replace with your OpenAI API key

    prompt_to_subject = f"Act as my assistant. Summarize this prompt shortly as a subject for an email: {email_prompt}"

    response = openai.Completion.create(
        engine='text-davinci-003',
        prompt=prompt_to_subject,
        max_tokens=1024,
        temperature=0.5,
        n=1,
        stop=None
    )

    return response.choices[0].text.strip()

def sending_mail(email_receiver, email_subject, email_body):
    receiver = email_receiver   #passwort for email only: gphradmrreneocck
    subject = email_subject
    body = email_body

    em = EmailMessage()
    em['From'] = email_sender
    em['To'] = receiver
    em['Subject'] = subject
    em.set_content(body)

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context = context) as smtp:
        smtp.login(email_sender, email_passwort)
        smtp.sendmail(email_sender, email_receiver, em.as_string())


def main():
    #for generate_email() we need a name to whom we write
    #and the prompt of the email
    target = "Mark"        #can it be changed to STT-module?
    email_prompt = "Can you change this custom prompt to our speach to text module?"        #can it be changed to STT-module?
     
    email_body = generate_email(target, email_prompt)
    email_subject = generate_subject_for_email(email_prompt)
    
    email_receiver = 'eduard.chalovskyy@gmail.com' 
    #email_receiver has to be extended with a function that will 
    # (1) get all contacts of the sender gmail account using google people api  
    # (2) ask chatgpt "which of the email adresses does belong to Mark"
    # have troubles using google api. tried three different approaches. it does not want to work..  
    

    sending_mail(email_receiver, email_subject, email_body)
    print(f'The following email was sent to {target}:')
    print(email_body)

if __name__ == '__main__':
    main()


#first try that does not work
def pull_contacts():
    gd_client = gdata.contacts.service.ContactsService()
    gd_client.email = email_sender
    gd_client.source = email_passwort
    gd_client.source = "abstractbinary.org-pull_contacts-1"
    gd_client.ProgrammaticLogin()
    query = gdata.contacts.service.ContactsQuery()
    query.max_results = 100
    contacts = gd_client.GetContactsFeed(query.ToUri())

    for entry in contacts.entry:
        nick = ""
        name = entry.title.text
        for email in entry.email:
            print('%s\t%s\t"%s" <%s>' % (nick, name, name, email.address))

#second try that does not work
def get_contacts():
    gd_client = gdata.contacts.service.ContactsService()
    gd_client.email = args[0]
    gd_client.password = getpass.getpass()
    gd_client.source = "abstractbinary.org-pull_contacts-1"
    gd_client.ProgrammaticLogin()

    query = gdata.contacts.service.ContactsQuery()
    query.max_results = 1000
    contacts = gd_client.GetContactsFeed(query.ToUri())
    for entry in contacts.entry:
        nick = ""
        name = entry.title.text
        for email in entry.email:
            print('%s\t%s\t"%s" <%s>' % (nick, name, name, email.address))
