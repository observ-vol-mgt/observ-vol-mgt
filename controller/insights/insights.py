import logging
import numpy as np

logger = logging.getLogger(__name__)


def generate_insights(signals):
    corr_matrix = signals.metadata["corr_matrix"]
    threshold = 0.999

    # conclude the list of signals that cab be reduces
    # -=--=-=-==--=
    #
    # Select upper triangle of correlation matrix
    upper = corr_matrix.where(np.triu(np.ones(corr_matrix.shape), k=1).astype(bool))

    # Find index and column name of features with correlation greater than 0.999
    corr_features = [column for column in upper.columns if any(upper[column] > threshold)]
    insights = f"We can reduce: {corr_features}"

    logging.info(f"\n\n{insights}\n")

    return insights
