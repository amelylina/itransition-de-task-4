from pathlib import Path
import logging

import src.aggregate as ag
from src.load import load_all_files
from src.dashboard import generate_dashboard

log = logging.getLogger(__name__)

MAIN_DIR = Path(__file__).parent
DATA_FOLDER = MAIN_DIR / 'data'

def process_dir(dir:str):
    users,user_alias,orders,books =load_all_files(folder_path=DATA_FOLDER/dir)
    return {
        'name': dir,
        'unique_users': len(user_alias),
        'unique_author_sets': ag.unique_athors(books),
        'most_pop_author': ag.most_pop_author(orders, books),
        'top_customer_alias': user_alias[ag.top_customer_id(orders, users)],
        'daily_revenue': ag.daily_revenue(orders),
        'top_days': ag.top_n_days(orders),
    }

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    dirs = ['DATA1','DATA2','DATA3']
    results = []
    for dir in dirs:
        log.info(f"Starting processing directory : {dir}")
        results.append(process_dir(dir))

    generate_dashboard(results, output_path='dashboard.html')

    log.info(f"Dashboard saved")