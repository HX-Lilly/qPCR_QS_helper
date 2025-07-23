import streamlit as st
import pandas as pd

# User selects PCR type
pcr_type = st.selectbox("Select qPCR type", ["singleplex", "duplex", "triplex", "quadruplex"])

uploaded_file = st.file_uploader("Upload 384-well plate layout (CSV)", type=["csv"])

if uploaded_file:
    # Read the input file, shouldn't have header
    plate_df = pd.read_csv(uploaded_file, header=None)

    # A–P 16 rows
    row_labels = [chr(ord('A') + i) for i in range(16)]
    plate_df.index = row_labels[:len(plate_df)]

    plate_df.columns = [str(i + 1) for i in range(plate_df.shape[1])]

    # Long format
    long_df = plate_df.reset_index().melt(id_vars='index', var_name='Column', value_name='Sample Name')
    long_df.rename(columns={'index': 'Row'}, inplace=True)

    # Create well IDs like A1, B2...
    long_df['Well'] = long_df['Row'] + long_df['Column']
    long_df = long_df[['Well', 'Sample Name']]

    long_df = long_df[long_df['Sample Name'].notna() & (long_df['Sample Name'] != '')]

    repeat_map = {"singleplex": 1, "duplex": 2, "triplex": 3, "quadruplex": 4}
    n_repeat = repeat_map[pcr_type]
    long_df = long_df.loc[long_df.index.repeat(n_repeat)].reset_index(drop=True)

    st.subheader("Input for QuantStudio")
    st.dataframe(long_df)

    csv = long_df.to_csv(index=False).encode('utf-8')
    st.download_button("Download CSV", csv, "long_format_output.csv", "text/csv")
