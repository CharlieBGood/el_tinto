import re

def replace_words_in_sentence(sentence, user=None):
    """Replace all the words from sentence that match the replace structure with user info."""
    if user:
        matches = re.findall('\{[a-zA-Z_]+\}', sentence)
    
        for match in matches:
            sentence = replace_word(sentence, match, user)
        
        return re.sub(' +', ' ', sentence)
    
    else:
        return sentence


def replace_word(sentence, word, model):
    """Replace a word for its model equivalent"""
    disallowed_characters = ['{', '}']
    
    attribute = word
    
    for character in disallowed_characters:
        attribute = attribute.replace(character, '')
    
    model_attribute = getattr(model, attribute)
    
    return sentence.replace(word, model_attribute)

def get_email_headers(headers):
    """Get email headers as dict"""

    email_headers = {}

    for header in headers:
        if header['name'] == 'EMAIL-ID':
            email_headers['email_id'] = int(header['value'])
        if header['name'] == 'EMAIL-TYPE':
            email_headers['email_type'] = header['value']
        if header['name'] == 'To':
            email_headers['user_email'] = header['value']

    return email_headers