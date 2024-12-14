import json
import os
import pandas as pd


def mb(b):
    return round(b / 1024 / 1024, 2)

def explore_dataset_size(df, filename, result_filename):
    print(df.head())
    size_on_disk = os.path.getsize(filename)
    ram_size_by_columns = df.memory_usage(deep=True)
    total_ram_size = ram_size_by_columns.sum()
    print(f'Dataset size on disk [{mb(size_on_disk)} MB]')
    print(f'Dataset size in RAM [{mb(total_ram_size)} MB]')
    columns_info = []
    for key in df.dtypes.keys():
        relative_size = round((ram_size_by_columns[key] / total_ram_size) * 100, 2)
        size = mb(ram_size_by_columns[key])
        columns_info.append({
            'name': key,
            'relative_size': relative_size,
            'size_in_MB': size,
            'type': df.dtypes[key]
        })
        print(f'[{key}] size [{size} MB], relative size [{relative_size} %] type [{df.dtypes[key]}]')

    columns_info.sort(key=lambda x: x['size_in_MB'], reverse=True)

    with open(result_filename, 'w') as f:
        json.dump(columns_info, f, default=str)



def optimize_object(df):
    converted_obj = pd.DataFrame()
    dataset_obj = df.select_dtypes(include=['object']).copy()

    for col in dataset_obj.columns:
        num_unique_values = len(dataset_obj[col].unique())
        num_total_values = len(dataset_obj[col])
        if num_unique_values / num_total_values < 0.5:
            print(f'Convert [{col}] to category type')
            converted_obj.loc[:, col] = dataset_obj[col].astype('category')
        else:
            converted_obj.loc[:, col] = dataset_obj[col]

    print(f'Old object columns size is [{mb(dataset_obj.memory_usage(deep=True)).sum()}]')
    print(f'New object columns size is [{mb(converted_obj.memory_usage(deep=True)).sum()}]')
    return converted_obj

def optimize_integers(df):
    dataset_int = df.select_dtypes(include=['int'])
    converted_int = dataset_int.apply(pd.to_numeric, downcast='unsigned')

    compare_ints = pd.concat([dataset_int.dtypes, converted_int.dtypes], axis=1)
    compare_ints.columns = ['before', 'after']
    compare_ints.apply(pd.Series.value_counts)
    print(f'Old int columns size is [{mb(dataset_int.memory_usage(deep=True)).sum()}]')
    print(f'New int columns size is [{mb(converted_int.memory_usage(deep=True)).sum()}]')
    print(compare_ints)
    return converted_int

def optimize_floats(df):
    dataset_float = df.select_dtypes(include=['float'])
    converted_float = dataset_float.apply(pd.to_numeric, downcast='float')

    print(f'Old float columns size is [{mb(dataset_float.memory_usage(deep=True)).sum()}]')
    print(f'New float columns size is [{mb(converted_float.memory_usage(deep=True)).sum()}]')

    compare_floats = pd.concat([dataset_float.dtypes, converted_float.dtypes], axis=1)
    compare_floats.columns = ['before', 'after']
    compare_floats.apply(pd.Series.value_counts)
    print(compare_floats)

    return converted_float


#dataset from https://www.kaggle.com/datasets/irkaal/foodcom-recipes-and-reviews?select=recipes.csv
df = pd.read_csv('./recipes.csv')
explore_dataset_size(df, './recipes.csv', './results/without_optimization_column_infos.json')
optimized_dataset = df.copy()


converted_obj = optimize_object(df)
converted_int = optimize_integers(df)
converted_float = optimize_floats(df)

optimized_dataset[converted_obj.columns] = converted_obj
optimized_dataset[converted_int.columns] = converted_int
optimized_dataset[converted_float.columns] = converted_float

explore_dataset_size(optimized_dataset, './recipes.csv', './results/with_optimization_column_infos.json')



need_column = dict()
column_names = ['AuthorName', 'CookTime', 'PrepTime',
                 'TotalTime', 'DatePublished', 'RecipeCategory',
                 'ReviewCount', 'Calories', 'SugarContent', 'Keywords']
opt_dtypes = optimized_dataset.dtypes
for key in df.columns:
    need_column[key] = opt_dtypes[key]
    print(f"{key}:{opt_dtypes[key]}")

with open('receipts_data_types.json', mode="w") as file:
    dtype_json = need_column.copy()
    for key in dtype_json.keys():
        dtype_json[key] = str(dtype_json[key])

    json.dump(dtype_json, file)