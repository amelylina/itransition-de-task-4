import pandas as pd

def top_n_days(orders:pd.DataFrame,n:int=5):
    top_days = daily_revenue(orders).sort_values(ascending=False).head(n)
    return top_days

def unique_athors(books:pd.DataFrame):
    return books['author_set'].nunique()

def most_pop_author(orders:pd.DataFrame,books:pd.DataFrame):
    merged = (orders.merge(right=books[['id','author_set']],left_on='book_id',right_on='id'))['author_set']
    top_set = merged.value_counts().index[0]
    return ', '.join(top_set)

def top_customer_id(orders:pd.DataFrame, users:pd.DataFrame):
    merged = (orders.merge(right=users[['id','root_id']],left_on='user_id',right_on='id'))[['root_id','paid_price']]
    grouped = merged.groupby('root_id')['paid_price'].sum()
    return grouped.idxmax()

def daily_revenue(orders:pd.DataFrame):
    daily = orders.groupby('date')['paid_price'].sum().sort_index()
    return daily