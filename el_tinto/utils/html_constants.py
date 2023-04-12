LINE_BREAKER = '<hr style="width: 100%; border: 1px solid #5044e4; margin: 40px 0 20px 0;" />'

SHARE_NEWS = """
    <table style="border-spacing: 0; margin: 30px 0 0 0">
        <tbody>
          <tr>
            <td style="padding: 0">
              <img
                  src="https://el-tinto-utils.s3.amazonaws.com/share_individual_news/MENU_BG_SHARE.png"
                  style="display: block; height:40px"
                >
            </td>
            <td style="padding: 0">
              <a
                ses:tags="type:WBP; tinto_block_entry:{{id}}"
                href="https://{{env}}eltinto.xyz/noticias/{{id}}/" class="" 
                target="_blank"
              >
                <img
                  src="https://el-tinto-utils.s3.amazonaws.com/share_individual_news/MENU_BG_WEB.png"
                  style="display: block; height:40px"
                >
              </a>
            </td>
            <td style="padding: 0">
              <a
                ses:tags="type:FB; tinto_block_entry:{{id}}"
                href="https://www.facebook.com/sharer/sharer.php?u=https://{{env}}eltinto.xyz/noticias/{{id}}/"
                target="_blank"
              >
                <img
                  src="https://el-tinto-utils.s3.amazonaws.com/share_individual_news/MENU_BG_FB.png"
                  style="display: block; height:40px"
                >
              </a>
            </td>
            <td style="padding: 0">
              <a
                ses:tags="type:TW; tinto_block_entry:{{id}}"
                href="https://twitter.com/intent/tweet?text={{title}}%20@ElTinto_%20https://{{env}}eltinto.xyz/noticias/{{id}}/"
                target="_blank"
              >
                <img
                  src="https://el-tinto-utils.s3.amazonaws.com/share_individual_news/MENU_BG_TW.png"
                  style="display: block; height:40px"
                >
              </a>
            </td>
            <td style="padding: 0">
              <a
                ses:tags="type:WP; tinto_block_entry:{{id}}"
                href="https://api.whatsapp.com/send?text={{title}}%20https://{{env}}eltinto.xyz/noticias/{{id}}/"
                target="_blank"
              >
                <img
                  src="https://el-tinto-utils.s3.amazonaws.com/share_individual_news/MENU_BG_WA.png"
                  style="display: block; height:40px"
                >
              </a>
            </td>
          </tr>
        </tbody>
    </table>
"""

INVITE_USERS_MESSAGE = """
Suscríbete%20a%20El%20Tinto%20y%20ayúdame%20a%20aumentar%20mi%20número%20de%20recomendados%20😁%0A%0A*¡Recuerda%20que%20tienes%20que%20abrir%20por%20lo%20menos%20un%20correo%20para%20que%20cuentes%20como%20mi%20referido!*%0A%0AEl%20Tinto,%20historias%20importantes%20para%20gente%20ocupada.%20
"""