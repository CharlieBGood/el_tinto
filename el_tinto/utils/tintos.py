def generate_tinto_html(tinto):
    """
    Generate html based on the TintoBlocks related to the passed Tinto

    :params:
    tinto: Tinto object

    :return:
    html: str
    """
    html = ''

    for tinto_block_entry in tinto.tintoblocksentries_set.all():
        html += tinto_block_entry.display_html

    return html
