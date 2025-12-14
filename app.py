import streamlit as st
import pandas as pd
from capability_logic import CapabilityAnalysis
from capability_plots import create_six_pack
import io

st.set_page_config(page_title="Capability 6-Pack", layout="wide")

st.markdown("""
<style>
    @media print {
        .stSidebar, .stFileUploader, .stSelectbox, .stNumberInput, .stButton, header, footer {
            display: none !important;
        }
        .block-container {
            padding: 0 !important;
            margin: 0 !important;
        }
    }
</style>
""", unsafe_allow_html=True)

st.title("Capability 6-Pack Report Generator")
st.markdown("Upload a CSV file, define limits, and generate a printable report.")

uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)

        # Sidebar for configuration
        st.sidebar.header("Configuration")

        columns = df.columns.tolist()
        selected_column = st.sidebar.selectbox("Select Dimension (Column)", columns)

        st.sidebar.subheader("Specification Limits")
        lsl = st.sidebar.number_input("Lower Spec Limit (LSL)", value=float(df[selected_column].min()), format="%.4f")
        usl = st.sidebar.number_input("Upper Spec Limit (USL)", value=float(df[selected_column].max()), format="%.4f")

        use_target = st.sidebar.checkbox("Specify Target?", value=False)
        target_val = 0.0
        if use_target:
            target_val = st.sidebar.number_input("Target Value", value=0.0, format="%.4f")

        if st.sidebar.button("Generate Report"):
            if lsl >= usl:
                st.error("LSL must be less than USL.")
            else:
                # Perform analysis
                target = target_val if use_target else None
                analysis = CapabilityAnalysis(df[selected_column], lsl, usl, target)

                # Create Charts
                fig = create_six_pack(analysis, title=f"Six Pack Report: {selected_column}")

                # Display
                st.pyplot(fig)

                # Add a download button for the plot?
                # Streamlit usually handles this via the "Save image" right click,
                # but we can offer a PDF download if we wanted to go the extra mile.
                # For now, print to PDF is the requirement.

                st.success("Report generated! Use your browser's 'Print' function (Ctrl+P) and 'Save as PDF'.")

    except Exception as e:
        st.error(f"Error processing file: {e}")

else:
    st.info("Please upload a CSV file to get started.")
