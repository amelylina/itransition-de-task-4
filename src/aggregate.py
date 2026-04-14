import pandas as pd

def top_n_days(orders:pd.DataFrame,n:int=5):
    top_days = daily_revenue(orders).sort_values(ascending=False).head(n)
    return top_days

def unique_authors(books:pd.DataFrame):
    return books['author_set'].nunique()

def most_pop_author(orders:pd.DataFrame,books:pd.DataFrame):
    merged = (orders.merge(right=books[['id','author_set']],left_on='book_id',right_on='id'))['author_set']
    grouped = merged.groupby('author_set')['quantity'].sum()
    top_set = grouped.idxmax()
    return ', '.join(sorted(top_set))

def top_customer_id(orders:pd.DataFrame, users:pd.DataFrame):
    merged = (orders.merge(right=users[['id','root_id']],left_on='user_id',right_on='id'))[['root_id','paid_price']]
    grouped = merged.groupby('root_id')['paid_price'].sum()
    return grouped.idxmax()

def daily_revenue(orders:pd.DataFrame):
    daily = orders.groupby('date')['paid_price'].sum().sort_index()
    return daily

def unique_users(users:pd.DataFrame):
    return users['root_id'].nunique()
