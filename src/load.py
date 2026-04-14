import pandas as pd
from pathlib import Path
from dateutil import parser
import yaml
from itertools import combinations

from src.unionfind import UnionFind

#------------------------------------------------------------
# USERS
def build_alias(users: pd.DataFrame):
    uf = UnionFind()

    for uid in users['id']:
        uf.find(uid)

    fields = ['name', 'address', 'phone', 'email']
    for combo in combinations(fields, 3):
        groups = users.groupby(list(combo))['id'].agg(list)
        pairs = groups[groups.str.len() > 1].dropna().tolist()
        for group in pairs:
            for i in range(1, len(group)):
                uf.union(group[0], group[i])

    alias = {}
    for uid in uf.parent.keys():
        root = uf.find(uid)
        if root not in alias:
            alias[root] = {uid}
        else:
            alias[root].add(uid)

    return alias, uf

def load_process_users(users_path:Path):
    users = pd.read_csv(users_path)
    users['phone'] = users['phone'].str.replace(r'\D', '', regex=True)

    alias, uf = build_alias(users)
    users['root_id'] = users['id'].apply(uf.find)
    users = users.drop_duplicates(subset='id')
    return users, alias

#------------------------------------------------------------
# ORDERS
def parse_price(price:str):
    eur = False
    if 'E' in price or '€' in price: eur = True
    num_list = []
    cur_num = ""
    for char in price:
        if char.isdigit():
            cur_num+= char
        else:
            if cur_num!="": num_list.append(cur_num)
            cur_num = ""

    if cur_num !="": num_list.append(cur_num)

    final = float('.'.join(num_list))

    if eur: return round(1.2 * final,2)
    return round(final,2)

def parse_time(t:str):
    t = t.replace(',',' , ')
    t = t.replace('A.M.','AM')
    t = t.replace('P.M.','PM')
    dt = parser.parse(t)
    return dt

def load_process_orders(orders_path:Path):
    orders = pd.read_parquet(orders_path)
    orders['unit_price'] = orders['unit_price'].apply(parse_price)
    orders['timestamp'] = orders['timestamp'].apply(parse_time)
    orders['year'] = orders['timestamp'].dt.year
    orders['month'] = orders['timestamp'].dt.month
    orders['day'] = orders['timestamp'].dt.day
    orders['date'] = orders['timestamp'].dt.date
    orders['paid_price'] = orders['unit_price'] * orders['quantity']
    orders = orders.drop_duplicates(subset='id')
    return orders

#------------------------------------------------------------
# BOOKS
def load_process_books(books_path:Path):
    with open(books_path, 'r') as f:
        books_data = yaml.safe_load(f)
    books = pd.DataFrame(books_data)
    books.columns = books.columns.str.strip(':')
    books['author_set'] = books['author'].apply(lambda a: frozenset(name.strip() for name in a.split(',')))
    books = books.drop_duplicates(subset='id')
    return books

#------------------------------------------------------------
# MAIN LOADING STUFF
def load_all_files(folder_path:Path):
    user_path = folder_path / 'users.csv'
    order_path = folder_path / 'orders.parquet'
    books_path = folder_path / 'books.yaml'

    users, user_alias = load_process_users(user_path)
    orders = load_process_orders(order_path)
    books = load_process_books(books_path)
    return users, user_alias, orders, books