#  Copyright 2024 IBM, Inc.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
import json
import logging
import pandas as pd
from sentence_transformers.losses import CosineSimilarityLoss
from setfit import SetFitModel, SetFitTrainer
from common.signal import Signal, Signals

logger = logging.getLogger(__name__)


def metadata_classification(config, signals):
    classified_signals = Signals(metadata=signals.metadata, signals=[])

    labeled_corpus_file = config.few_shot_classification_file
    model = config.model

    # Loading zero-shot samples from file
    with open(labeled_corpus_file) as f:
        data = json.load(f)

    # Extract sentences and labels
    sentences = [item[0] for item in data]
    labels = [item[1] for item in data]

    # Initialize the few-shot classification
    fit_model = SetFitModel.from_pretrained(model)

    train_data_df = pd.DataFrame({
        'sentence': sentences,
        'label': labels
    })

    eval_data_df = pd.DataFrame(columns=['sentence', 'label'])

    for signal in signals:
        eval_data_df.append({"sentence": f"{signal.metadata}"})

    trainer = SetFitTrainer(
        model=fit_model,
        train_dataset=train_data_df,
        eval_dataset=eval_data_df,
        loss_class=CosineSimilarityLoss,
        num_iterations=10,
        column_mapping={"sentence": "text", "label": "label"},
    )

    trainer.train()
    metrics = trainer.evaluate()
    logging.debug(f"Metrics: {metrics}")

    return classified_signals
