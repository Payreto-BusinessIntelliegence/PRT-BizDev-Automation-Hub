import streamlit as st
import base64
from PIL import Image

bd_logo = Image.open('assets/home/bd_logo.png')

def image_to_base64(image):
    import io
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

bd_logo_base64 = image_to_base64(bd_logo)

st.set_page_config(page_title="BD Automation Hub", layout="wide",)

st.markdown(
    f"""
    <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; padding-top: 20px;">
        <img src="data:image/png;base64,{bd_logo_base64}" alt="BD Logo" style="width: 700px; margin-bottom: 10px;">
        <h1 style='color: #fee6aa; margin: 0;'>BizDev Automation Hub</h1>
    </div>
    """, 
    unsafe_allow_html=True
)

st.write("")
st.write("""Lorem ipsum odor amet, consectetuer adipiscing elit. Odio hac tempus semper augue sollicitudin dolor. Massa commodo facilisis fringilla, orci maecenas efficitur felis consequat donec. Bibendum est id suspendisse ut metus vitae. Dis sodales metus fusce fringilla elit semper imperdiet sapien? Risus erat velit duis nam penatibus dui commodo nibh. Quisque maecenas curae porttitor tortor litora justo sollicitudin rhoncus amet. Enim ut malesuada felis mi ad dignissim ullamcorper litora. Egestas diam accumsan justo nascetur pellentesque ornare magnis volutpat. Penatibus felis tortor leo nostra dignissim efficitur aptent dui.

Sodales lectus metus sed finibus; blandit purus vivamus bibendum. Suspendisse vivamus nisi quam efficitur maximus tempus etiam. Consequat convallis duis luctus dui parturient nisl aptent. Nulla aliquam nec laoreet dolor purus bibendum. Nulla facilisis et ornare nascetur vulputate hendrerit. Interdum cras morbi, dapibus tempus auctor tincidunt congue.

Ornare sem arcu magna eros ad dui viverra litora nascetur. Bibendum sed sem lobortis condimentum diam. Ac penatibus tempus; erat cursus ante scelerisque. Leo pellentesque lacus lectus malesuada amet sociosqu. Nullam netus augue amet habitasse maecenas scelerisque. Convallis fringilla dignissim finibus auctor arcu tortor ut. Porta vel mattis risus; lectus mauris duis. Justo tortor bibendum ridiculus duis non ac eget curae.

Nisl pharetra rutrum orci eu mus sed ad. Quis nisl dis nullam; pellentesque facilisis vitae. Diam litora laoreet eleifend inceptos elementum diam nisi. Id quisque sed gravida; amet dapibus pellentesque non laoreet. Pretium etiam nibh eu pharetra dictum. Elit facilisi iaculis facilisis nibh sed. Sociosqu curae volutpat facilisi dapibus magna parturient. Maecenas a torquent hac lorem placerat potenti fames dapibus.

Porta sit fames sagittis ornare magnis nullam. Rhoncus tellus vulputate ligula nisi libero placerat parturient. Bibendum magnis feugiat sed dapibus diam sed, sapien ullamcorper. Integer laoreet mauris magna ex ridiculus ex. Nibh habitant pharetra nec lobortis vestibulum platea posuere? Ornare ridiculus natoque neque praesent himenaeos curae imperdiet purus conubia. Lobortis sociosqu tellus blandit aliquet torquent. Fermentum fermentum eros pretium sapien facilisis mus mattis dolor.

Amet interdum tortor felis penatibus risus nisi. Quisque tristique habitant per netus eu natoque leo! Nostra nostra habitasse malesuada ac; ullamcorper arcu venenatis. Tincidunt mi diam adipiscing aliquam mus metus, auctor habitant. Turpis gravida pretium aenean tempus feugiat ultricies sociosqu. Condimentum vel mus fusce elit auctor duis risus. Nisi consequat augue finibus cubilia massa fames. Donec vivamus aenean convallis nulla elementum.

Integer euismod aptent egestas in montes risus ut ipsum. Sapien efficitur nostra efficitur luctus lacinia scelerisque nibh. Dis nullam elementum non suspendisse euismod bibendum ridiculus laoreet. Placerat interdum phasellus morbi ad; parturient volutpat. Mauris tristique faucibus mus hac justo placerat semper proin. Dapibus ex vestibulum accumsan dolor, purus vitae purus faucibus. Purus aliquet per venenatis etiam mollis class adipiscing.

Nascetur habitant elit integer penatibus proin, at rutrum elit malesuada. Nibh morbi ut aliquam lectus facilisi mauris dui. Est vehicula quisque sem maximus scelerisque condimentum orci aliquet. Netus libero magnis eros sodales sapien ad. Laoreet eleifend maximus risus non placerat primis. Natoque tellus nisi congue justo non erat.

Tincidunt integer consequat vulputate imperdiet auctor nibh class eget. Class suspendisse a ut dapibus ante ipsum aliquam. Augue conubia faucibus est a morbi molestie sit nisi. Magna vitae sapien finibus, nisi duis nunc. Pellentesque vestibulum efficitur aptent dictumst adipiscing lobortis egestas. Pulvinar posuere potenti luctus posuere est magna himenaeos blandit. Ut ornare sem phasellus; non eu duis eros. Consequat scelerisque ex facilisis nec massa curabitur. Ut augue in purus per, tellus elementum tellus.

Pulvinar maximus finibus porttitor pulvinar nisl rhoncus enim erat nisi. Himenaeos facilisis molestie sit fermentum, cursus odio rutrum viverra. Morbi nulla quis interdum nisl ultricies eu. Urna vivamus sem; auctor pretium nunc justo. Iaculis ad adipiscing tincidunt arcu molestie fusce in dignissim senectus. Natoque tellus penatibus integer aliquam consectetur. Sem ridiculus augue dis justo facilisis, curae ullamcorper. Inceptos sociosqu volutpat at leo nec. Nam facilisi nam libero curabitur tortor tellus dis nam finibus.""")
