import pandas as pd
import matplotlib.pyplot as plt

# Assuming your CSV file is named 'best_investors.csv'
df = pd.read_csv('best_investors.csv')

# List of factors
factors = ['strat', 'risk', 'time', 'influence']

# Creating subplots
fig, axes = plt.subplots(nrows=2, ncols=2, figsize=(10, 8))

# Custom bin configurations and x-axis limits for each factor
bins = {'strat': 4, 'risk': 10, 'time': 10, 'influence': 10}
xlims = {'strat': (0, 5), 'risk': (0, 1), 'time': (0, 1), 'influence': (0, 1)}

# Colors for each histogram
hist_colors = ['skyblue', 'lightcoral', 'lightgreen', 'lightyellow']

# Plotting histograms for each factor on separate subplots
for i, factor in enumerate(factors):
    row = i // 2
    col = i % 2

    if factor == 'strat':
        categories = df[factor].unique()
        category_counts = df[factor].value_counts().reindex(categories, fill_value=0)
        axes[row, col].bar(categories, category_counts, color=hist_colors[i])
    else:
        axes[row, col].hist(df[factor], bins=bins.get(factor, 10), edgecolor='black', color=hist_colors[i])

    axes[row, col].set_title(f'{factor.capitalize()} Distribution')
    axes[row, col].set_xlabel(factor.capitalize() if factor != 'strat' else 'Strategy Category')
    axes[row, col].set_ylabel('Frequency')

    # Set x-axis limits if provided
    xlim = xlims.get(factor)
    if xlim:
        axes[row, col].set_xlim(xlim)

# Adjusting layout
plt.suptitle('Highest Profits - Factor Distributions')
plt.tight_layout(rect=[0, 0, 1, 0.96])  # Adjusting title position
plt.show()
