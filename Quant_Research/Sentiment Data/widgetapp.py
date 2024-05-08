import streamlit as st

def embed_myfxbook_widget():
    st.markdown(
        """
        <iframe src="https://widgets.myfxbook.com/widgets/fxOutlook.html?type=0&symbols=,1,2,3,4,5,6,7,8,9,10,11,12,13,14,17,20,24,25,26,27,28,29,46,47,48,49,51,103,107" 
                width="100%" 
                height="600" 
                frameborder="0" 
                scrolling="no" 
                style="border:none;">
        </iframe>
        """,
        unsafe_allow_html=True
    )

def main():
    st.title('Myfxbook Outlook Widget')
    embed_myfxbook_widget()

if __name__ == "__main__":
    main()
