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
import copy

from setfit import SetFitModel, Trainer
from datasets import Dataset

logger = logging.getLogger(__name__)


def finetune_from_basemodel(base_model, labeled_corpus_file, few_shot_pretrained_model_directory):
    # Loading zero-shot samples from file
    with open(labeled_corpus_file) as f:
        data = json.load(f)

    # Extract sentences and labels
    sentences = [item[0] for item in data]
    labels = [item[1] for item in data]

    # Initialize the few-shot classification
    fit_model = SetFitModel.from_pretrained(base_model)

    train_data_df = pd.DataFrame({
        'sentence': sentences,
        'label': labels
    })

    train_data_dataset = Dataset.from_pandas(train_data_df)

    trainer = Trainer(
        model=fit_model,
        train_dataset=train_data_dataset,
        eval_dataset=None,
        column_mapping={"sentence": "text", "label": "label"},
    )

    trainer.train()
    # metrics = trainer.evaluate()
    # logging.debug(f"Metrics: {metrics}")

    # saves the model locally
    trainer.model.save_pretrained(few_shot_pretrained_model_directory)


def metadata_classification(config, signals):
    classified_signals = copy.copy(signals)

    labeled_corpus_file = config.few_shot_classification_file
    base_model = config.base_model
    few_shot_pretrained_model_directory = config.few_shot_pretrained_model_directory

    # check if pretrained_model exists, if so use it, if not fine-tune the base model
    try:
        model = SetFitModel.from_pretrained(
            few_shot_pretrained_model_directory)
    except Exception:
        logger.info(f"pretrained_model not found in {few_shot_pretrained_model_directory}"
                    f", fine-tuning from base model {base_model}")
        finetune_from_basemodel(
            base_model, labeled_corpus_file, few_shot_pretrained_model_directory)
        logger.info(
            f"fine-tuning is done, model saved to {few_shot_pretrained_model_directory}")
        model = SetFitModel.from_pretrained(
            few_shot_pretrained_model_directory)

    eval_data_list = []

    for index, signal in enumerate(signals):
        eval_data_list.append(signal.metadata)

    # evaluate the model on the signals data
    predictions = model.predict(eval_data_list)
    for index, signal in enumerate(signals):
        classified_signals.signals[index].metadata["classification"] = predictions[index]
        classified_signals.signals[index].metadata["classification_score"] = "N/A"

    return classified_signals
