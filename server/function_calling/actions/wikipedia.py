#pip3 install wikipedia-api
import wikipediaapi 
import re

def getWikiPageInfo(title: str, language: str, number_of_sentences: int) -> str:
    wiki_wiki = wikipediaapi.Wikipedia('MyProjectName (merlin@example.com)', 'en')
    if (language == "german"):
        wiki_wiki = wikipediaapi.Wikipedia('MyProjectName (merlin@example.com)', 'de')
        
    page = wiki_wiki.page(title)
    if not page.exists():
        if language == "german":
            return "Zu diesem Thema habe ich keine Informationen."
        else:
            return "I have no information on this subject."
    summary = page.summary
    tokens = re.split(r'(?<=[.!?])\s+', summary)
    return " ".join(tokens[:number_of_sentences])

#print(getWikiPageInfo("Mountainbike", "english", 1))
#print()
#print(getWikiPageInfo("Mountainbike", "german", 4))
