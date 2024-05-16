import streamlit as st

# Set the page layout to wide
st.set_page_config(layout="wide")

def embed_myfxbook_widget():
    html_code = """
    <div>
        <script class="powered" type="text/javascript"
                src="https://widgets.myfxbook.com/scripts/fxOutlook.js?type=1&symbols=,1,2,3,4,5,6,7,8,9,10,11,12,13,14,17,20,24,25,26,27,28,29,46,47,48,49,51,103,107"></script>
    </div>
    <div style="font-size: 10px">
        <a href="https://www.myfxbook.com" title="" class="myfxbookLink" target="_self" rel="noopener">
            Powered by Myfxbook.com
        </a>
    </div>

    <script type="text/javascript">
        showOutlookWidget()
    </script>
    """

    st.components.v1.html(html_code)

def main():
    st.title('Myfxbook Outlook Widget')
    embed_myfxbook_widget()

if __name__ == "__main__":
    main()
