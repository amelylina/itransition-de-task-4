import base64
import io
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates


def generate_chart_base64(daily_revenue):
    fig, ax = plt.subplots(figsize=(14, 4.5))

    dates = list(daily_revenue.index)
    values = list(daily_revenue.values)

    ax.plot(dates, values, color='#41975E', linewidth=1.5, alpha=0.85)
    ax.fill_between(dates, values, alpha=0.08, color='#41975E')

    ax.set_xlabel('Date', fontsize=10, color='#6b7280', labelpad=10)
    ax.set_ylabel('Revenue ($)', fontsize=10, color='#6b7280', labelpad=10)
    ax.tick_params(colors='#9ca3af', labelsize=9)

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#e5e7eb')
    ax.spines['bottom'].set_color('#e5e7eb')

    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'${x:,.0f}'))
    fig.autofmt_xdate(rotation=45)
    ax.grid(axis='y', linestyle='--', alpha=0.3, color='#d1d5db')

    fig.tight_layout()

    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=150, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    buf.seek(0)
    return base64.b64encode(buf.read()).decode('utf-8')


def build_tab_html(result, tab_index):
    chart_b64 = generate_chart_base64(result['daily_revenue'])

    top_days_rows = ''
    for i, (date, revenue) in enumerate(result['top_days'].items()):
        rank = i + 1
        top_days_rows += f'''
            <tr>
                <td class="rank">#{rank}</td>
                <td class="date-cell">{date}</td>
                <td class="revenue-cell">${revenue:,.2f}</td>
            </tr>'''

    alias_ids = sorted(result['top_customer_alias'])
    alias_str = '['+', '.join(str(a) for a in alias_ids)+']'

    return f'''
    <div class="tab-content" id="tab-{tab_index}">
        <div class="kpi-grid">
            <div class="kpi-card">
                <div class="kpi-label">Unique Users</div>
                <div class="kpi-value">{result['unique_users']:,}</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-label">Unique Author Sets</div>
                <div class="kpi-value">{result['unique_author_sets']:,}</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-label">Most Popular Author(s)</div>
                <div class="kpi-value author-name">{result['most_pop_author']}</div>
            </div>
            <div class="kpi-card wide">
                <div class="kpi-label">Best Buyer (all aliases)</div>
                <div class="kpi-value alias-list">{alias_str}</div>
            </div>
        </div>
        <div class="section-card">
            <h2 class="section-title">Top 5 Days by Revenue</h2>
            <table class="revenue-table">
                <thead>
                    <tr>
                        <th>Rank</th>
                        <th>Date</th>
                        <th>Revenue</th>
                    </tr>
                </thead>
                <tbody>
                    {top_days_rows}
                </tbody>
            </table>
        </div>
        <div class="section-card">
            <h2 class="section-title">Daily Revenue</h2>
            <div class="chart-container">
                <img src="data:image/png;base64,{chart_b64}" alt="Daily Revenue Chart" />
            </div>
        </div>
    </div>
    '''

def generate_dashboard(results, output_path:Path):
    dashboard_path = output_path / 'index.html'

    tab_buttons = ''
    for i, r in enumerate(results):
        active = ' active' if i == 0 else ''
        tab_buttons += f'<button class="tab-btn{active}" onclick="switchTab({i})">{r["name"]}</button>\n'

    tab_contents = ''
    for i, r in enumerate(results):
        tab_contents += build_tab_html(r, i)

    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Book Sales Dashboard</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
    *, *::before, *::after {{
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }}

    body {{
        font-family: 'DM Sans', sans-serif;
        background: #f0f2f5;
        color: #1a1a2e;
        min-height: 100vh;
    }}

    .dashboard-header {{
        background: linear-gradient(135deg, #84b59f 0%, #8f95d3 100%);
        padding: 2rem 3rem;
        color: white;
    }}

    .dashboard-header h1 {{
        font-size: 1.75rem;
        font-weight: 700;
        letter-spacing: -0.02em;
    }}

    .dashboard-header p {{
        color: white;
        margin-top: 0.25rem;
        font-size: 0.9rem;
    }}

    .tab-bar {{
        display: flex;
        gap: 0;
        background: #E4E8E6;
        padding: 0 3rem;
        border-bottom: 2px solid #aebab5;
    }}

    .tab-btn {{
        font-family: 'DM Sans', sans-serif;
        font-size: 0.9rem;
        font-weight: 600;
        padding: 0.75rem 1.5rem;
        border: none;
        background: transparent;
        color: #64748b;
        cursor: pointer;
        border-bottom: 2px solid transparent;
        margin-bottom: -2px;
        transition: all 0.2s ease;
    }}

    .tab-btn:hover {{
        color: #94a3b8;
    }}

    .tab-btn.active {{
        color: #6c69bc;
        border-bottom-color: #6c69bc;
    }}

    .main-content {{
        max-width: 1200px;
        margin: 2rem auto;
        padding: 0 2rem;
    }}

    .tab-content {{
        display: none;
    }}

    .tab-content.visible {{
        display: block;
    }}

    .kpi-grid {{
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 1rem;
        margin-bottom: 1.5rem;
    }}

    .kpi-card {{
        background: white;
        border-radius: 10px;
        padding: 1.5rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.06);
        border: 1px solid #e8eaed;
    }}

    .kpi-card.wide {{
        grid-column: 1 / -1;
    }}

    .kpi-label {{
        font-size: 0.78rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #6b7280;
        margin-bottom: 0.5rem;
    }}

    .kpi-value {{
        font-size: 1.85rem;
        font-weight: 700;
        color: #1a1a2e;
    }}

    .kpi-value.author-name {{
        font-size: 1.3rem;
    }}

    .kpi-value.alias-list {{
        font-family: 'JetBrains Mono', monospace;
        font-size: 1rem;
        font-weight: 500;
        color: #374151;
        word-break: break-all;
    }}

    .section-card {{
        background: white;
        border-radius: 10px;
        padding: 1.5rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.06);
        border: 1px solid #e8eaed;
        margin-bottom: 1.5rem;
    }}

    .section-title {{
        font-size: 1rem;
        font-weight: 600;
        color: #374151;
        margin-bottom: 1rem;
        padding-bottom: 0.75rem;
        border-bottom: 1px solid #f3f4f6;
    }}

    .revenue-table {{
        width: 100%;
        border-collapse: collapse;
    }}

    .revenue-table th {{
        text-align: left;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #9ca3af;
        padding: 0.6rem 1rem;
        border-bottom: 1px solid #f3f4f6;
    }}

    .revenue-table td {{
        padding: 0.75rem 1rem;
        border-bottom: 1px solid #f9fafb;
        font-size: 0.95rem;
    }}

    .revenue-table tr:last-child td {{
        border-bottom: none;
    }}

    .revenue-table .rank {{
        color: #9ca3af;
        font-weight: 600;
        font-size: 0.85rem;
    }}

    .revenue-table .date-cell {{
        font-family: 'JetBrains Mono', monospace;
        font-weight: 500;
        color: #1a1a2e;
    }}

    .revenue-table .revenue-cell {{
        font-family: 'JetBrains Mono', monospace;
        font-weight: 500;
        color: #059669;
    }}

    .chart-container {{
        text-align: center;
    }}

    .chart-container img {{
        max-width: 100%;
        height: auto;
        border-radius: 6px;
    }}

    @media (max-width: 768px) {{
        .kpi-grid {{
            grid-template-columns: 1fr;
        }}
        .dashboard-header {{
            padding: 1.5rem;
        }}
        .tab-bar {{
            padding: 0 1rem;
        }}
        .main-content {{
            padding: 0 1rem;
        }}
    }}
</style>
</head>
<body>

<div class="dashboard-header">
    <h1>Book Sales Dashboard</h1>
    <p>Revenue analytics and customer insights</p>
</div>

<div class="tab-bar">
    {tab_buttons}
</div>

<div class="main-content">
    {tab_contents}
</div>

<script>
function switchTab(index) {{
    document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('visible'));
    document.querySelectorAll('.tab-btn').forEach(el => el.classList.remove('active'));

    document.querySelectorAll('.tab-content')[index].classList.add('visible');
    document.querySelectorAll('.tab-btn')[index].classList.add('active');
}}

switchTab(0);
</script>

</body>
</html>'''

    with open(dashboard_path, 'w') as f:
        f.write(html)