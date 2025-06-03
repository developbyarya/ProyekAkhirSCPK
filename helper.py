import numpy as np
import plotly.express as px

def split_empasis(arr: np.array):
    emphasis_set = set()
    for item in arr:
        parts = [e.strip() for e in item.split(';')]
        emphasis_set.update(parts)

    # If you want it as a list
    emphasis_list = sorted(emphasis_set)
    return emphasis_list

def count_matches(emphasis_string, selected):
    emphases = [e.strip() for e in emphasis_string.split(';')]
    return sum(1 for e in emphases if e in selected)

def budget_score(expense, min_budget, max_budget):
    if expense < min_budget or expense > max_budget:
        return 0
    return 1 - ((expense - min_budget) / (max_budget - min_budget + 1e-6))  # avoid division by zero


def gaussian_score(x, mu, sigma=1000):  # sigma = sensitivity
    return np.exp(- ((x - mu) ** 2) / (2 * sigma ** 2))

def heatmap(df, column):
    df = df.copy()
    state_name_to_code = {
    'Alabama': 'AL', 'Alaska': 'AK', 'Arizona': 'AZ', 'Arkansas': 'AR',
    'California': 'CA', 'Colorado': 'CO', 'Connecticut': 'CT', 'Delaware': 'DE',
    'Florida': 'FL', 'Georgia': 'GA', 'Hawaii': 'HI', 'Idaho': 'ID',
    'Illinois': 'IL', 'Indiana': 'IN', 'Iowa': 'IA', 'Kansas': 'KS',
    'Kentucky': 'KY', 'Louisiana': 'LA', 'Maine': 'ME', 'Maryland': 'MD',
    'Massachusetts': 'MA', 'Michigan': 'MI', 'Minnesota': 'MN', 'Mississippi': 'MS',
    'Missouri': 'MO', 'Montana': 'MT', 'Nebraska': 'NE', 'Nevada': 'NV',
    'New Hampshire': 'NH', 'New Jersey': 'NJ', 'New Mexico': 'NM',
    'New York': 'NY', 'North Carolina': 'NC', 'North Dakota': 'ND',
    'Ohio': 'OH', 'Oklahoma': 'OK', 'Oregon': 'OR', 'Pennsylvania': 'PA',
    'Rhode Island': 'RI', 'South Carolina': 'SC', 'South Dakota': 'SD',
    'Tennessee': 'TN', 'Texas': 'TX', 'Utah': 'UT', 'Vermont': 'VT',
    'Virginia': 'VA', 'Washington': 'WA', 'West Virginia': 'WV',
    'Wisconsin': 'WI', 'Wyoming': 'WY'
    }
    df['state_code'] = df['state'].map(state_name_to_code)
    df = df.dropna(subset=['state_code'])
    state_avg_sat = df.groupby('state_code')[column].mean().reset_index()
    state_avg_sat = df.groupby('state_code')[column].mean().reset_index()

    # Create Plotly chart
    fig = px.choropleth(
        state_avg_sat,
        locations='state_code',
        locationmode='USA-states',
        color=column,
        color_continuous_scale='Viridis',
        scope='usa',
        # labels={column: 'Avg SAT Score'},
        title='Average SAT Scores by U.S. State'
    )
    return fig
