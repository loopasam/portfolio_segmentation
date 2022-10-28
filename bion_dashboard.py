import streamlit as st
import pandas as pd

from feature_mode import feature_mode
from filter_mode import filter_mode


@st.cache
def read_data():
    data = pd.read_excel('data/subset_segmentation.xlsx', engine='openpyxl')
    data['Duration of Investment'] = data['Duration of Investment'].dt.year
    data['NAV'] = data['NAV'] * 100

    weight_df = data[['Company', 'NAV']]
    weight = {}
    for i, row in weight_df.iterrows():
        company = row['Company']
        nav = row['NAV']
        weight[company] = nav
    return data, weight


def main():
    st.set_page_config(page_title="BION Portfolio", layout="wide", initial_sidebar_state="expanded")

    data, weight = read_data()

    mode = st.sidebar.selectbox('Mode', ['Feature', 'Filter'])
    st.sidebar.write('<hr>', unsafe_allow_html=True)
    if mode == 'Feature':
        feature_mode(data)
    else:
        filter_mode(data)


if __name__ == '__main__':
    main()
