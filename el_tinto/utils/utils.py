import re

def replace_words_in_sentence(sentence, user):
    """Replace all the words from sentence that match the replace structure with user info."""

    matches = re.findall('\{[a-zA-Z_]+\}', sentence)
    
    for match in matches:
        sentence = replace_word(sentence, match, user)
    
    return re.sub(' +', ' ', sentence)


def replace_word(sentence, word, model):
    """Replace a word for its model equivalent"""
    
    disallowed_characters = ['{', '}']
    
    attribute = word
    
    for character in disallowed_characters:
        attribute = attribute.replace(character, '')
    
    model_attribute = getattr(model, attribute)
    
    return sentence.replace(word, model_attribute)
    