LINE_BREAKER = '<hr style="width: 100%; border: 1px solid #5044e4; margin: 40px 0 20px 0;" />'

SHARE_NEWS = """
    <table style="width: 40%; margin: 30px auto 60px auto;">
        <tbody>
          <tr>
            <td>
              <a
                ses:tags="type:WBP"
                href="https://{{env}}eltinto.xyz/noticias/{{id}}/" class="" target="_blank"
              >
                <img
                  src="https://el-tinto-utils.s3.amazonaws.com/el_tinto_cursor.png"
                  style="width: 50px; height: auto; margin: 0 auto; display: block;"
                >
              </a>
            </td>
            <td>
              <a
                ses:tags="type:FB"
                href="https://www.facebook.com/sharer/sharer.php?u=https://{{env}}eltinto.xyz/noticias/{{id}}/"
                target="_blank"
              >
                <img
                  src="https://el-tinto-utils.s3.amazonaws.com/facebook_icon.png"
                  style="width: 40px; height: auto; margin: 0 auto; display: block;"
                >
              </a>
            </td>
            <td>
              <a
                ses:tags="type:TW"
                href="https://twitter.com/intent/tweet?text={{title}}%20https://{{env}}eltinto.xyz/noticias/{{id}}/"
                target="_blank"
              >
                <img
                  src="https://el-tinto-utils.s3.amazonaws.com/twitter_icon.png"
                  style="width: 40px; height: auto; margin: 0 auto; display: block;"
                >
              </a>
            </td>
            <td>
              <a
                ses:tags="type:WP"
                href="https://api.whatsapp.com/send?text={{title}}%20https://{{env}}eltinto.xyz/noticias/{{id}}/"
                target="_blank"
              >
                <img
                  src="https://el-tinto-utils.s3.amazonaws.com/whatsapp_icon.png"
                  style="width: 40px; height: auto; margin: 0 auto; display: block;"
                >
              </a>
            </td>
          </tr>
        </tbody>
    </table>
"""
