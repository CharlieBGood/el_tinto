import re


def replace_words_in_sentence(sentence, user=None):
    """Replace all the words from sentence that match the replacement structure with user info."""
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


def replace_social_media_buttons(html):
    """Replace social media buttons in html"""
    social_media_buttons_html = """
        <img style="display: block; margin-left: auto; margin-right: auto; margin-top: 60px"' 
        src="https://el-tinto-utils.s3.amazonaws.com/el_tinto_social_media_share.gif" 
        alt="el_tinto_social_media_share_giff" width="50%" height="auto"/><h3 style="text-align: center; 
        margin-top: 30px;"><strong>¿Te gustó el Tinto de hoy y quieres compartirlo?</strong></h3><table 
        style="width: 40%; margin: 30px auto 60px auto;"><tbody><tr><td><a ses:tags="type:WBP" 
        href="https://eltinto.xyz/el-tinto/?date={{social_media_date}}" class="" target="_blank">
        <img src="https://el-tinto-utils.s3.amazonaws.com/el_tinto_cursor.png" 
        style="width: 50px; height: auto; margin: 0 auto; display: block;"></a></td><td><a ses:tags="type:FB" 
        href="https://www.facebook.com/sharer/sharer.php?u=https://eltinto.xyz/el-tinto/?date={{social_media_date}}" 
        class="" target="_blank"><img src="https://el-tinto-utils.s3.amazonaws.com/facebook_icon.png" 
        style="width: 40px; height: auto; margin: 0 auto; display: block;"></a></td><td><a ses:tags="type:TW" 
        href="https://twitter.com/intent/tweet?text={{tweet}}%20https://eltinto.xyz/el-tinto/?date={{social_media_date}}" 
        class="" target="_blank"><img src="https://el-tinto-utils.s3.amazonaws.com/twitter_icon.png" 
        style="width: 40px; height: auto; margin: 0 auto; display: block;"></a></td><td><a ses:tags="type:WP" 
        href="https://api.whatsapp.com/send?text={{tweet}}%20https://eltinto.xyz/el-tinto/?date={{social_media_date}}" 
        class="" target="_blank"><img src="https://el-tinto-utils.s3.amazonaws.com/whatsapp_icon.png" 
        style="width: 40px; height: auto; margin: 0 auto; display: block;"></a></td></tr></tbody></table>
        <hr style="width: 100%; border: 6px solid #382c9c; margin: 20px 0 0 0">
        <hr style="width: 100%; border: 6px solid #5044e4; margin: 0 0 20px 0">
    """

    html.replace("__social_media_buttons__", social_media_buttons_html)


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


def get_string_days(numeric_days):
    """Get the string value of the days based on its numeric representation"""

    if numeric_days == ['0', '1', '2', '3', '4']:
        string_days = 'entre semana'

    elif numeric_days == ['5', '6']:
        string_days = 'los fines de semana'

    elif numeric_days == ['0', '1', '2', '3', '4', '5', '6']:
        string_days = 'todos los días'

    else:

        new_preferred_days = [DAY_OF_THE_WEEK_MAP.get(day) for day in numeric_days]

        last_day = ''

        if len(new_preferred_days) > 1:
            last_day = ' y ' + new_preferred_days.pop()

        string_days = 'en los días ' + ', '.join(new_preferred_days) + last_day

    return string_days


# Constants

EVENT_TYPE_CLICK = 'Click'
EVENT_TYPE_OPEN = 'Open'

EVENT_TYPES = [EVENT_TYPE_CLICK, EVENT_TYPE_OPEN]

DAY_OF_THE_WEEK_MAP = {
    '0': 'lunes',
    '1': 'martes',
    '2': 'miércoles',
    '3': 'jueves',
    '4': 'viernes',
    '5': 'sábado',
    '6': 'domingo'
}
