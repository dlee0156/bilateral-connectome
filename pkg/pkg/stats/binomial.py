import numpy as np
from scipy.stats import chi2_contingency, fisher_exact
from statsmodels.stats.contingency_tables import mcnemar
from statsmodels.stats.proportion import test_proportions_2indep

from .fisher_exact_nonunity import fisher_exact_nonunity


def binom_2samp(x1, n1, x2, n2, null_odds, method="fisher"):
    if x1 == 0 or x2 == 0:
        # logging.warn("One or more counts were 0, not running test and returning nan")
        return np.nan, np.nan
    if null_odds != 1 and method != "fisher":
        raise ValueError("Non-unity null odds only works with Fisher's exact test")

    cont_table = np.array([[x1, n1 - x1], [x2, n2 - x2]])
    if method == "fisher" and null_odds == 1.0:
        stat, pvalue = fisher_exact(cont_table)
    elif method == "fisher" and null_odds != 1.0:
        stat, pvalue = fisher_exact_nonunity(cont_table, null_odds=null_odds)
    elif method == "chi2":
        stat, pvalue, _, _ = chi2_contingency(cont_table)
    elif method == "agresti-caffo":
        stat, pvalue = test_proportions_2indep(
            x1,
            n1,
            x2,
            n2,
            method="agresti-caffo",
            compare="diff",
            alternative="two-sided",
        )
    else:
        raise ValueError()

    return stat, pvalue


def binom_2samp_paired(x1, x2):
    x1 = x1.astype(bool)
    x2 = x2.astype(bool)

    # TODO these two don't actually matter at all for McNemar's test...
    n_both = (x1 & x2).sum()
    n_neither = ((~x1) & (~x2)).sum()

    n_only_x1 = (x1 & (~x2)).sum()
    n_only_x2 = ((~x1) & x2).sum()

    cont_table = [[n_both, n_only_x2], [n_only_x1, n_neither]]
    cont_table = np.array(cont_table)

    bunch = mcnemar(cont_table)
    stat = bunch.statistic
    pvalue = bunch.pvalue

    misc = {}
    misc["n_both"] = n_both
    misc["n_neither"] = n_neither
    misc["n_only1"] = n_only_x1
    misc["n_only2"] = n_only_x2

    return stat, pvalue, misc
