import streamlit as st
import plotly.graph_objects as go


def show_feature_selector(data):
    features = data.columns.values.tolist()
    features.remove('NAV')
    selector = st.sidebar.selectbox('Features', features)
    return selector


def feature_data(data, selector):
    # subset = data[selector]
    subset = data[['NAV', selector]]
    return subset


def get_pie_chart(groups, desc):
    labels = groups.index
    values = groups
    pie = go.Figure(data=[go.Pie(labels=labels, values=values)])
    pie.update_layout(title=desc)
    return pie


def plot_feature_data(groups_n, groups_weight):
    pie_n = get_pie_chart(groups_n, 'by number of companies')
    pie_weight = get_pie_chart(groups_weight, 'by portfolio weight')

    config = {'modeBarButtonsToRemove': ['zoom', 'pan', 'select', 'zoomIn', 'zoomOut', 'autoScale', 'resetScale', 'lasso2d'], 'displaylogo': False}

    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(pie_weight, use_container_width=True, config=config)

    with col2:
        st.plotly_chart(pie_n, use_container_width=True, config=config)


def feature_mode(data):
    selector = show_feature_selector(data)
    st.title(selector)

    # Filter to the selected level
    subset = feature_data(data, selector)
    # st.write(subset)

    # Compute based on the selection
    groups_n = data.groupby(by=[selector])['NAV'].count()
    # st.write(groups_n)

    groups_weight = subset.groupby(by=[selector])['NAV'].sum()
    # st.write(groups_weight)

    # Plot the data
    plot_feature_data(groups_n, groups_weight)

