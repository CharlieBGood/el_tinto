def global_variables(request):
    """
    Define the global variables to be used on templates.
    This function is called from settings.TEMPLATES
    """
    return {
        "el_tinto_logotype_url": "https://el-tinto-utils.s3.amazonaws.com/logos/el_tinto_text_b.png",
        "el_tinto_image_url": "https://el-tinto-utils.s3.amazonaws.com/logos/el_tinto_imagen.png",
        "el_tinto_image_no_space_url": "https://el-tinto-utils.s3.amazonaws.com/logos/el_tinto_imagen_sin_espacios.png",
        "el_tinto_imagotype_url": "https://el-tinto-utils.s3.amazonaws.com/logos/el_tinto_imagotipo.png",
        "el_tinto_favicon_url": "https://el-tinto-utils.s3.amazonaws.com/logos/favicon.ico",
    }