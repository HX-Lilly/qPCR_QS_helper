import streamlit as st
import pandas as pd

st.title("PCR Plate Processor")

# PCR type selection
pcr_type = st.selectbox(
    "Select PCR Type",
    options=["singleplex", "duplex", "triplex", "quadruplex"]
)

# File uploader for plate layout (CSV)
uploaded_file = st.file_uploader("Upload 384-well plate layout (CSV)", type=["csv"])

if uploaded_file:
    # Assume the layout is a 16x24 grid (standard 384-well layout)
    plate_df = pd.read_csv(uploaded_file, index_col=0)
    
    # Melt to long format
    long_df = plate_df.reset_index().melt(id_vars=plate_df.index.name, var_name="Column", value_name="Sample")
    long_df.rename(columns={plate_df.index.name: "Row"}, inplace=True)

    # Create well position (e.g., A1, B2)
    long_df["Well"] = long_df["Row"].astype(str) + long_df["Column"].astype(str)
    long_df = long_df[["Well", "Sample"]]

    # Drop empty wells
    long_df = long_df[long_df["Sample"].notna() & (long_df["Sample"] != "")]

    # Repeat rows based on PCR type
    repeat_map = {"singleplex": 1, "duplex": 2, "triplex": 3, "quadruplex": 4}
    n_repeat = repeat_map[pcr_type]
    long_df = long_df.loc[long_df.index.repeat(n_repeat)].reset_index(drop=True)

    # Output table
    st.subheader("Resulting Long Format Table")
    st.dataframe(long_df)

    # Downloadable output
    csv = long_df.to_csv(index=False).encode('utf-8')
    st.download_button("Download CSV", csv, "long_format_output.csv", "text/csv")
