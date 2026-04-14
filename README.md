## Implementation notes

Code is not extremely universal as the task was to just load from the given data, so:
- in parsing prices I first ran a check to see which characters appear. For example ',' is not in any of the prices hence why I'm not accounting for that in parsing function. I was considering using regex, but I would need to make a pattern for each appearing price variants, so the decision was made to use a more robust function with splitting strings.
- timestamps were a mess as well and I believe simple pandas builtin to_datetime wouldn't work without formating the strings in advance, but that would again require mapping all the patterns.
- I ran a check on which columns have null values, and found out only the insignificant ones (like shipment in orders) have nulls. 'Address' column has nulls, but I decided against filling missing rows, as it could mess up the grouping user reconcilation system. Comparing users still runs smoothly as I also check for other column groupings like 'name,phone,email' etc.

## Running

pip install -r requirements.txt
python main.py

Dashboard is written to docs/index.html, also hosted at github-pages of this repo.

Data expected at data/DATA1/, data/DATA2/, data/DATA3/ — each with users.csv, orders.parquet, books.yaml.
