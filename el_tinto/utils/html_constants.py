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

INTERNAL_HYPERLINK = """
    <a id={tag} style='color: inherit !important; font-size: inherit !important; text-decoration: none !important'>
    {html}
    </a>
"""

INVITE_USERS_MESSAGE = """
%C2%A1Hola%21%20Quer%C3%ADa%20recomendarte%20El%20Tinto%20%E2%98%95%EF%B8%8F%2C%20un%20newsletter%20diario%20curado%20
con%20los%20medios%20m%C3%A1s%20rigurosos%20de%20Colombia%20y%20el%20mundo%20que%20te%20mantiene%20informado%20en%20
s%C3%B3lo%205%20minutos.%20%0A%0ATe%20puedes%20suscribir%20ac%C3%A1%3A%0A
"""

