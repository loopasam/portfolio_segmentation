import streamlit as st
import pandas as pd
import plotly.graph_objects as go

data = pd.read_excel('data/test_dataset.xlsx', engine='openpyxl')
# st.write(data)

bg = data.groupby(by=['Therapeutic area'])['Company'].count()
bg = bg.to_frame()
bg = bg.reset_index()
bg = bg.rename({'Company': 'n_bg'}, axis=1)

add_selectbox = st.sidebar.selectbox(
    "How would you like to be contacted?",
    ["Email", "Home phone", "Mobile phone"]
)

development = st.sidebar.multiselect(
    'Dev. status',
    ['Advanced', 'Preclinical', 'Mid stage'],
    ['Advanced', 'Preclinical', 'Mid stage']
)

# st.write('You selected:', development)
subset = data[data['Development'].isin(development)]

assets = st.multiselect(
    'Asset type',
    ['Platform', 'Single asset'],
    ['Platform', 'Single asset']
)

# st.write('You selected:', development)
subset = subset[subset['Assets'].isin(assets)]

selection = subset.groupby(by=['Therapeutic area'])['Company'].count()
selection = selection.to_frame()
selection = selection.reset_index()
selection = selection.rename({'Company': 'n_selection'}, axis=1)

# st.write(bg)
# st.write(selection)

dataset = pd.merge(bg, selection, on='Therapeutic area', how='outer')
dataset = dataset.fillna(value=0)
dataset['n_non_selection'] = dataset['n_bg'] - dataset['n_selection']

# st.write(dataset)
# st.bar_chart(data=dataset, x='Therapeutic area', y=['n_selection', 'n_non_selection'])

fig = go.Figure(data=[
    go.Bar(name='n_selection', x=dataset['Therapeutic area'], y=dataset['n_selection'], marker_color='salmon'),
    go.Bar(name='n_non_selection', x=dataset['Therapeutic area'], y=dataset['n_non_selection'], marker_color='lightgray')
])
fig.update_layout(barmode='stack', showlegend=False)

pie = go.Figure(data=[go.Pie(values=[dataset['n_selection'].sum(), dataset['n_non_selection'].sum()])])
pie.update_traces(marker=dict(colors=['salmon', 'lightgray']))
pie.update_layout(showlegend=False)


col1, col2 = st.columns(2)
with col1:
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.plotly_chart(pie, use_container_width=True)


# st.plotly_chart(fig)
