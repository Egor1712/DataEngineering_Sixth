import json
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

column_names = ['AuthorName', 'CookTime', 'PrepTime',
                'TotalTime', 'DatePublished', 'RecipeCategory',
                'ReviewCount', 'Calories', 'SugarContent', 'Keywords']

with open('./receipts_data_types.json', 'r+', encoding='utf8') as f:
    data_types = json.load(f)

df = pd.read_csv('./recipes.csv', usecols=lambda x: x in column_names, dtype=data_types)
df['DatePublished'] = pd.to_datetime(df['DatePublished'])
df['year'] = df["DatePublished"].dt.year
df['month'] = df["DatePublished"].dt.month
print(df.head())

plt.figure(figsize=(20, 5))
plt.plot(df.groupby(df["DatePublished"].dt.date)['AuthorName'].count())
plt.xlabel('Date Published')
plt.ylabel('Receipts count')
plt.show()
plt.figure(figsize=(30, 10))
df['RecipeCategory'].value_counts()[:10, ].plot(kind='bar', title='RecipeCategory')
plt.show()
df['CookTime'].value_counts()[:10, ].plot(kind='pie', autopct='%1.1f%%', title='CookTime')
plt.show()

plt.figure(figsize=(30, 15))
sns.heatmap(df.pivot_table(values='Calories', index=['year'], columns=['month'], aggfunc='mean', dropna=True))
plt.show()

df[df.SugarContent < df.SugarContent.mean()].plot.scatter(x='SugarContent', y='ReviewCount')
plt.show()

sns.displot(
    data=df.isna().melt(value_name="missing"),
    y="variable",
    hue="missing",
    multiple="fill"
)
plt.show()
