import pandas as pd

data = pd.read_excel('test_dataset.xlsx', engine='openpyxl')

bg = data.groupby(by=['Therapeutic area'])['Company'].count()
bg = bg.to_frame()
bg = bg.reset_index()
bg = bg.rename({'Company': 'n_bg'}, axis=1)


# development = ['Advanced', 'Preclinical']
development = ['Advanced']
subset = data[data['Development'].isin(development)]

selection = subset.groupby(by=['Therapeutic area'])['Company'].count()
selection = selection.to_frame()
selection = selection.reset_index()
selection = selection.rename({'Company': 'n_selection'}, axis=1)

dataset = pd.merge(selection, bg, on='Therapeutic area', how='outer')
dataset['n_non_selection'] = dataset['n_bg'] - dataset['n_selection']
dataset = dataset.fillna(value=0)
print(dataset)
