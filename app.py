import streamlit as st
import pandas as pd

# User selects PCR type
pcr_type = st.selectbox("Select PCR type", ["singleplex", "duplex", "triplex", "quadruplex"])

uploaded_file = st.file_uploader("Upload 384-well plate layout (CSV)", type=["csv"])

if uploaded_file:
    # Read the CSV (no headers expected)
    plate_df = pd.read_csv(uploaded_file, header=None)

    # Define row labels A–P for 16 rows
    row_labels = [chr(ord('A') + i) for i in range(16)]
    plate_df.index = row_labels[:len(plate_df)]

    # Add column numbers as strings (1–24)
    plate_df.columns = [str(i + 1) for i in range(plate_df.shape[1])]

    # Melt into long format
    long_df = plate_df.reset_index().melt(id_vars='index', var_name='Column', value_name='Sample')
    long_df.rename(columns={'index': 'Row'}, inplace=True)

    # Create well IDs like A1, B2...
    long_df['Well'] = long_df['Row'] + long_df['Column']
    long_df = long_df[['Well', 'Sample']]

    # Drop empty values
    long_df = long_df[long_df['Sample'].notna() & (long_df['Sample'] != '')]

    # Repeat rows based on PCR type
    repeat_map = {"singleplex": 1, "duplex": 2, "triplex": 3, "quadruplex": 4}
    n_repeat = repeat_map[pcr_type]
    long_df = long_df.loc[long_df.index.repeat(n_repeat)].reset_index(drop=True)

    # Display results
    st.subheader("Resulting Long Format Table")
    st.dataframe(long_df)

    # Download option
    csv = long_df.to_csv(index=False).encode('utf-8')
    st.download_button("Download CSV", csv, "long_format_output.csv", "text/csv")
