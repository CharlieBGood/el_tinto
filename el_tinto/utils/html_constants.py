LINE_BREAKER = '<hr style="width: 100%; border: 1px solid #5044e4; margin: 40px 0 20px 0;" />'

SHARE_NEWS = """
    <table style="border-spacing: 0; margin: 30px 0 0 0">
        <tbody>
          <tr>
            <td style="padding: 0">
              <img
                  src="https://el-tinto-utils.s3.amazonaws.com/share_individual_news/MENU_SHARE.png"
                  style="display: block;"
                >
            </td>
            <td style="padding: 0">
              <a
                href="https://{{env}}eltinto.xyz/noticias/{{id}}/" class="" 
                target="_blank"
              >
                <img
                  src="https://el-tinto-utils.s3.amazonaws.com/share_individual_news/MENU_WEB.png"
                  style="display: block;"
                >
              </a>
            </td>
            <td style="padding: 0">
              <a
                href="https://www.facebook.com/sharer/sharer.php?u=https://{{env}}eltinto.xyz/noticias/{{id}}/"
                target="_blank"
              >
                <img
                  src="https://el-tinto-utils.s3.amazonaws.com/share_individual_news/MENU_FB.png"
                  style="display: block;"
                >
              </a>
            </td>
            <td style="padding: 0">
              <a
                href="https://twitter.com/intent/tweet?text={{title}}%20@ElTinto_%20https://{{env}}eltinto.xyz/noticias/{{id}}/"
                target="_blank"
              >
                <img
                  src="https://el-tinto-utils.s3.amazonaws.com/share_individual_news/MENU_TW.png"
                  style="display: block;"
                >
              </a>
            </td>
            <td style="padding: 0">
              <a
                href="https://api.whatsapp.com/send?text={{title}}%20https://{{env}}eltinto.xyz/noticias/{{id}}/"
                target="_blank"
              >
                <img
                  src="https://el-tinto-utils.s3.amazonaws.com/share_individual_news/MENU_WA.png"
                  style="display: block;"
                >
              </a>
            </td>
          </tr>
        </tbody>
    </table>
"""
