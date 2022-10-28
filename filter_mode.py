import streamlit as st
import plotly.graph_objects as go
import pandas as pd


def show_filter_selectors(data, selected):

    selectors = {}

    excluded = ['Company']
    for feature in data:
        if feature not in excluded:
            feature_type = data[feature].dtype
            if feature_type == 'object':
                values = list(data[feature].unique())
                if feature in selected:
                    selected_vals = selected[feature]
                else:
                    selected_vals = values
                selector = st.sidebar.multiselect(feature, values, selected_vals)
                selectors[feature] = selector
            elif feature_type == 'int64' or feature_type == 'float64':
                feature_max = max(data[feature])
                feature_min = min(data[feature])
                selector = st.sidebar.slider(feature, feature_min, feature_max, (feature_min, feature_max))
                selectors[feature] = selector
    return selectors


def get_bar_chart(dataset, selection, non_selection, title):
    fig = go.Figure(data=[
        go.Bar(name='n_selection', x=dataset['Therapeutic area'], y=dataset[selection], marker_color='salmon'),
        go.Bar(name='n_non_selection', x=dataset['Therapeutic area'], y=dataset[non_selection],
               marker_color='lightgray')
    ])
    fig.update_layout(barmode='stack', showlegend=False, title=title)
    return fig


def get_pie_chart(dataset, selection, non_selection, title):
    pie = go.Figure(data=[go.Pie(values=[dataset[selection].sum(), dataset[non_selection].sum()])])
    pie.update_traces(marker=dict(colors=['salmon', 'lightgray']))
    pie.update_layout(showlegend=False, title=title)
    return pie


def plot_filer_data(dataset):

    fig = get_bar_chart(dataset, 'n_selection', 'n_non_selection', 'by number of companies')
    fig_w = get_bar_chart(dataset, 'w_selection', 'w_non_selection', 'by portfolio weight')

    pie = get_pie_chart(dataset, 'n_selection', 'n_non_selection', 'by number of companies')
    pie_w = get_pie_chart(dataset, 'w_selection', 'w_non_selection', 'by portfolio weight')

    config = {'displayModeBar': False}

    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(fig_w, use_container_width=True, config=config)
        st.plotly_chart(fig, use_container_width=True, config=config)

    with col2:
        st.plotly_chart(pie_w, use_container_width=True, config=config)
        st.plotly_chart(pie, use_container_width=True, config=config)


def filter_data(data, selectors):
    subset = data
    for selector in selectors:
        feature_type = data[selector].dtype
        if feature_type == 'object':
            subset = subset[subset[selector].isin(selectors[selector])]
        if feature_type == 'int64' or feature_type == 'float64':
            subset = subset[(subset[selector] <= selectors[selector][1]) & (subset[selector] >= selectors[selector][0])]
    return subset


# @st.cache
def get_bg(data):
    bg = data.groupby(by=['Therapeutic area'])['Company'].count()
    bg = bg.to_frame()
    bg = bg.reset_index()
    bg = bg.rename({'Company': 'n_bg'}, axis=1)

    w_bg = data.groupby(by=['Therapeutic area'])['NAV'].sum()
    w_bg = w_bg.to_frame()
    w_bg = w_bg.reset_index()
    w_bg = w_bg.rename({'NAV': 'w_bg'}, axis=1)

    return bg, w_bg


def filter_mode(data):
    # st.title('Portfolio Exposure')

    # Compute the background values
    bg, w_bg = get_bg(data)

    # Compute the list of reset values
    reset = {}
    excluded = ['Company']
    for feature in data:
        if feature not in excluded:
            feature_type = data[feature].dtype
            if feature_type == 'object':
                values = list(data[feature].unique())
                reset[feature] = values

    # Preset mode in place
    preset = st.sidebar.selectbox('Preset', ['Default', 'Selection'])
    if preset == 'Selection':
        selected = {'Orphan diseases': ['Yes'], 'Therapeutic area': ["CNS", "Autoimmune"]}
    else:
        selected = reset

    # Show the filters
    selectors = show_filter_selectors(data, selected)

    # Filter to the selected level
    subset = filter_data(data, selectors)

    # Compute based on the selection
    selection = subset.groupby(by=['Therapeutic area'])['Company'].count()
    selection = selection.to_frame()
    selection = selection.reset_index()
    selection = selection.rename({'Company': 'n_selection'}, axis=1)

    # Compute based on the selection
    selection_weight = subset.groupby(by=['Therapeutic area'])['NAV'].sum()
    selection_weight = selection_weight.to_frame()
    selection_weight = selection_weight.reset_index()
    selection_weight = selection_weight.rename({'NAV': 'w_selection'}, axis=1)

    # Assemble the final dataset
    dataset = pd.merge(bg, w_bg, on='Therapeutic area', how='outer')
    dataset = pd.merge(dataset, selection, on='Therapeutic area', how='outer')
    dataset = pd.merge(dataset, selection_weight, on='Therapeutic area', how='outer')
    dataset = dataset.fillna(value=0)
    dataset['n_non_selection'] = dataset['n_bg'] - dataset['n_selection']
    dataset['w_non_selection'] = dataset['w_bg'] - dataset['w_selection']
    # st.write(dataset)

    # Plot the data
    plot_filer_data(dataset)
