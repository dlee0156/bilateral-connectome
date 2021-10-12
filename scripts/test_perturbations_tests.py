#%% [markdown]
# ## Preliminaries
#%%

import time
from giskard.utils import get_random_seed

from pkg.data import (
    load_maggot_graph,
    load_network_palette,
    load_node_palette,
    select_nice_nodes,
)
from pkg.io import savefig
from pkg.plot import set_theme
from pkg.perturb import remove_edges
from pkg.stats import erdos_reyni_test

from graspologic.utils import binarize
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def stashfig(name, **kwargs):
    foldername = "er_test"
    savefig(name, foldername=foldername, **kwargs)


# %% [markdown]
# ## Load and process data
#%%

t0 = time.time()
set_theme()

network_palette, NETWORK_KEY = load_network_palette()
node_palette, NODE_KEY = load_node_palette()

#%%

mg = load_maggot_graph()
mg = select_nice_nodes(mg)
left_mg, right_mg = mg.bisect(lcc=True)


left_adj = left_mg.sum.adj
right_adj = right_mg.sum.adj
left_adj = binarize(left_adj)
right_adj = binarize(right_adj)

#%%

random_state = np.random.default_rng(8888)
adj = right_adj
n_sims = 2
effect_sizes = [0, 50, 100, 150, 200]
rows = []

tests = {"ER": erdos_reyni_test}
perturbations = {"Remove edges": remove_edges}

for perturbation_name, perturb in perturbations.items():
    for effect_size in effect_sizes:
        for sim in range(n_sims):
            seed = get_random_seed(random_state)
            perturb_adj = perturb(adj, effect_size=effect_size, random_state=seed)
            for test_name, test in tests.items():
                stat, pvalue, other = test(adj, perturb_adj)
                row = {
                    "stat": stat,
                    "pvalue": pvalue,
                    "other": other,
                    "test": test_name,
                    "perturbation": perturbation_name,
                    "effect_size": effect_size,
                    "sim": sim,
                }
                rows.append(row)

results = pd.DataFrame(rows)
#%%
results

#%%
fig, ax = plt.subplots(1, 1, figsize=(8, 6))
sns.histplot(data=results, ax=ax, x="pvalue", hue="effect_size", binwidth=0.001)