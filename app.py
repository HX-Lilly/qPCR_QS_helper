import streamlit as st
import pandas as pd

# User selects PCR type
pcr_type = st.selectbox("Select qPCR type", ["singleplex", "duplex", "triplex", "quadruplex"])

# Define how many target names are needed
repeat_map = {"singleplex": 1, "duplex": 2, "triplex": 3, "quadruplex": 4}
n_repeat = repeat_map[pcr_type]

# Ask user for target names
target_names = []
st.markdown(f"### Enter {n_repeat} target name(s):")
for i in range(n_repeat):
    name = st.text_input(f"Target {i+1} name", key=f"target_{i}")
    target_names.append(name)

# File uploader
uploaded_file = st.file_uploader("Upload 384-well plate layout (CSV)", type=["csv"])

if uploaded_file and all(target_names):
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

    # Remove empty cells
    long_df = long_df[long_df['Sample Name'].notna() & (long_df['Sample Name'] != '')]

    # Repeat rows for multiplexing
    long_df = long_df.loc[long_df.index.repeat(n_repeat)].reset_index(drop=True)

    # Assign target names
    long_df['Target Name'] = target_names * (len(long_df) // n_repeat)

    st.subheader("Input for QuantStudio")
    st.dataframe(long_df)

    csv = long_df.to_csv(index=False).encode('utf-8')
    st.download_button("Download CSV", csv, "long_format_output.csv", "text/csv")
