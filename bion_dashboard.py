import streamlit as st
import pandas as pd
import plotly.graph_objects as go


@st.cache
def read_data():
    data = pd.read_excel('data/subset_segmentation.xlsx', engine='openpyxl')
    data['Duration of Investment'] = data['Duration of Investment'].dt.year
    return data


def show_filter_selectors(data):
    selectors = {}
    excluded = ['Company']
    for feature in data:
        # st.write(f'{feature}: {data[feature].dtype}')
        if feature not in excluded:
            feature_type = data[feature].dtype
            if feature_type == 'object':
                values = data[feature].unique()
                selector = st.sidebar.multiselect(feature, values, values)
                selectors[feature] = selector
            elif feature_type == 'int64' or feature_type == 'float64':
                feature_max = max(data[feature])
                feature_min = min(data[feature])
                selector = st.sidebar.slider(feature, feature_min, feature_max, (feature_min, feature_max))
                selectors[feature] = selector
            # elif feature_type == 'datetime64[ns]':
            #     # feature_max = pd.to_datetime(max(data[feature]))
            #     feature_max = max(data[feature]).to_pydatetime()
            #     # feature_min = pd.to_datetime(min(data[feature]))
            #     feature_min = min(data[feature]).to_pydatetime()
            #     selector = st.sidebar.slider(feature, feature_min, feature_max, (feature_min, feature_max))
            #     selectors[feature] = selector
    return selectors


def plot_filer_data(dataset):
    fig = go.Figure(data=[
        go.Bar(name='n_selection', x=dataset['Therapeutic area'], y=dataset['n_selection'], marker_color='salmon'),
        go.Bar(name='n_non_selection', x=dataset['Therapeutic area'], y=dataset['n_non_selection'],
               marker_color='lightgray')
    ])
    fig.update_layout(barmode='stack', showlegend=False, title='Distribution within therapeutic areas')

    pie = go.Figure(data=[go.Pie(values=[dataset['n_selection'].sum(), dataset['n_non_selection'].sum()])])
    pie.update_traces(marker=dict(colors=['salmon', 'lightgray']))
    pie.update_layout(showlegend=False, title='Proportion of portfolio companies')

    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.plotly_chart(pie, use_container_width=True)


@st.cache
def get_bg(data):
    bg = data.groupby(by=['Therapeutic area'])['Company'].count()
    bg = bg.to_frame()
    bg = bg.reset_index()
    bg = bg.rename({'Company': 'n_bg'}, axis=1)
    return bg


def filter_data(data, selectors):
    subset = data
    for selector in selectors:
        feature_type = data[selector].dtype
        if feature_type == 'object':
            subset = subset[subset[selector].isin(selectors[selector])]
        if feature_type == 'int64' or feature_type == 'float64':
            subset = subset[(subset[selector] <= selectors[selector][1]) & (subset[selector] >= selectors[selector][0])]
    return subset


def show_feature_selector(data):
    features = data.columns.values
    selector = st.sidebar.selectbox('Features', features)
    return selector


def feature_data(data, selector):
    subset = data[selector]
    return subset


def plot_feature_data(groups):
    labels = groups.index
    values = groups

    pie = go.Figure(data=[go.Pie(labels=labels, values=values)])
    # pie.update_traces(marker=dict(colors=['salmon', 'lightgray']))
    pie.update_layout(title='Proportion of portfolio companies')
    # pie.update_traces(hoverinfo='label+percent', textinfo='value+percent')

    st.plotly_chart(pie, use_container_width=True)


def feature_mode(data):
    selector = show_feature_selector(data)
    st.title(selector)

    # Filter to the selected level
    subset = feature_data(data, selector)

    # Compute based on the selection
    groups = subset.groupby(subset).count()

    # Plot the data
    plot_feature_data(groups)


def filter_mode(data):
    st.title('Portfolio Exposure')
    selectors = show_filter_selectors(data)

    # Compute the background values
    bg = get_bg(data)

    # Filter to the selected level
    subset = filter_data(data, selectors)

    # Compute based on the selection
    selection = subset.groupby(by=['Therapeutic area'])['Company'].count()
    selection = selection.to_frame()
    selection = selection.reset_index()
    selection = selection.rename({'Company': 'n_selection'}, axis=1)

    # Assemble the final dataset
    dataset = pd.merge(bg, selection, on='Therapeutic area', how='outer')
    dataset = dataset.fillna(value=0)
    dataset['n_non_selection'] = dataset['n_bg'] - dataset['n_selection']

    # Plot the data
    plot_filer_data(dataset)


def main():
    st.set_page_config(
        page_title="BION Portfolio",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    data = read_data()

    # st.sidebar.subheader('Mode')
    mode = st.sidebar.selectbox('Mode', ['Feature', 'Filter'])
    st.sidebar.write('<hr>', unsafe_allow_html=True)
    if mode == 'Feature':
        feature_mode(data)
    else:
        filter_mode(data)


if __name__ == '__main__':
    main()
