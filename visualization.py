import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import ttest_ind 

file_path = '12.06.24 Tuj1 Rb NES Ck.xlsx' # replace with your own

df = pd.read_excel(file_path, sheet_name = 1)

# Extract groups and subgroups
df['Group'] = df['Condition'].str.extract(r'(\d+-\d)')
# print(df['Group'])
df['Subgroup'] = df['Condition'].str.extract(r'([a-d])')
# print(df['Subgroup'])

pivoted = df.pivot(index='Group', columns='Subgroup', values='TUJ1/DAPI')

# Plot the bar graph
pivoted.plot(kind='bar', figsize=(10, 6), width=0.7)

# Customize the plot
plt.title('TUJ1/DAPI Ratio by Group and Subgroup')
plt.ylabel('TUJ1/DAPI Ratio')
plt.xlabel('Group')
plt.xticks(rotation=45)
plt.legend(title='Subgroup')
plt.tight_layout()

# Show the plot
# plt.show()


# Calculate mean NESTIN/TUJ1 for each group
mean_values = df.groupby('Group')['TUJ1/DAPI'].mean()

# Perform t-tests between groups to calculate significance
groups = df['Group'].unique()
p_values = {}

for i, group1 in enumerate(groups):
    for j, group2 in enumerate(groups):
        if i < j:  # Avoid duplicate comparisons
            # Extract values for the two groups
            group1_values = df[df['Group'] == group1]['TUJ1/DAPI']
            group2_values = df[df['Group'] == group2]['TUJ1/DAPI']
            
            # Perform t-test
            t_stat, p_value = ttest_ind(group1_values, group2_values)
            p_values[(group1, group2)] = p_value

# Assign significance stars based on p-values
def significance_stars(p):
    if p < 0.001:
        return '***'
    elif p < 0.01:
        return '**'
    elif p < 0.05:
        return '*'
    else:
        return 'ns'

significance = {key: significance_stars(p) for key, p in p_values.items()}
print(significance)

# Plot the mean NESTIN/TUJ1 ratio for each group with significance annotations
plt.figure(figsize=(10, 6))
x_positions = range(len(mean_values))
plt.bar(x_positions, mean_values, color='skyblue', alpha=0.7, edgecolor='black')

# Add labels and annotations
plt.xticks(x_positions, mean_values.index, rotation=45)
plt.title('Mean TUJ1/DAPI Ratio by Group with Significance')
plt.ylabel('Mean TUJ1/DAPI Ratio')
plt.xlabel('Group')

# Annotate significance between groups (example: adding significance above bars)
for (group1, group2), p in p_values.items():
    if significance[(group1, group2)] != 'ns':
        x1, x2 = groups.tolist().index(group1), groups.tolist().index(group2)
        y, h, col = mean_values.max() + 0.1, 0.05, 'black'
        plt.plot([x1, x1, x2, x2], [y, y + h, y + h, y], lw=1.5, c=col)
        plt.text((x1 + x2) * 0.5, y + h, significance[(group1, group2)], ha='center', va='bottom', color=col)

plt.tight_layout()
plt.show()
