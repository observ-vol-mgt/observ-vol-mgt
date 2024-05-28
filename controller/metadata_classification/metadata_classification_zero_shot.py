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
from transformers import pipeline
from common.signal import Signal, Signals

logger = logging.getLogger(__name__)


def metadata_classification(config, signals):
    classified_signals = Signals(metadata=signals.metadata, signals=[])

    # Initialize the zero-shot classification pipeline
    # Load the zero-shot classification model
    classifier = pipeline(task="zero-shot-classification", model="facebook/bart-large-mnli")

    # Loading zero-shot samples from file
    with open(config.zero_shot_classification_file) as f:
        data = json.load(f)

    # Extract sentences and labels
    sentences = [item[0] for item in data]
    labels = [item[1] for item in data]

    # Perform zero-shot classification
    results = classifier(sentences, labels)

    # Print results for existing sentences
    for sentence, result in zip(sentences, results):
        logger.debug(f"Sentence: {sentence}")
        logger.debug(f"True Label: {data[sentences.index(sentence)][1]}")
        logger.debug(f"Predicted Label: {result['labels'][0]}")
        logger.debug(f"Score: {result['scores'][0]}")
        logger.debug(f"\n")

    # metadata classification for signals
    for signal in signals:
        # extract features from the signal
        classification_result = metadata_classification_signal(classifier, labels, signal)
        classified_signal = signal
        classified_signal.metadata['classification'] = classification_result['labels'][0]
        classified_signal.metadata['classification_score'] = classification_result['scores'][0]
        classified_signals.signals.append(classified_signal)

    return classified_signals


def metadata_classification_signal(classifier, labels, signal):
    metadata = f"{signal.metadata}"
    result = classifier(metadata, labels)
    logger.debug(f"Metadata for classify: {metadata}")
    logger.debug(f"Predicted Label: {result['labels'][0]}")
    logger.debug(f"Score: {result['scores'][0]}")
    return result
