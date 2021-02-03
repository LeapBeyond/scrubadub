import re
import nltk
import copy
import pandas as pd
import pathlib
import warnings

from nltk.tokenize.api import TokenizerI

from sklearn.feature_extraction import DictVectorizer
from sklearn.preprocessing import LabelEncoder
from sklearn.linear_model import LogisticRegression

from typing import Optional, List, Dict, Any, Generator, Union, Collection, NamedTuple

from .base import Detector
from ..filth.base import Filth
from ..filth.known import KnownFilth
from ..filth.address import AddressFilth
from ..modelling.serialisation import estimator_from_json, estimator_to_json

DocumentName = Optional[Union[str, int]]


class TokenPosition(NamedTuple):
    beg: int
    end: int


class TokenTuple(NamedTuple):
    doc_name: DocumentName
    token: str
    span: TokenPosition


class TokenTupleWithLabel(NamedTuple):
    doc_name: DocumentName
    token: str
    span: TokenPosition
    label: str


class TokenTupleWithPredictedTrueLabels(NamedTuple):
    doc_name: DocumentName
    token: str
    span: TokenPosition
    predicted_label: str
    true_label: str


# TODO: fix mypy errors

class SklearnDetector(Detector):
    """This is the base of a detector that tokenises text, turns that into features (including features from
    next/previous words), and runs this through a serialised ML model.
    """
    name = 'sklearn'
    punct_languages = {
        'cs': 'czech',
        'da': 'danish',
        'nl': 'dutch',
        'en': 'english',
        'et': 'estonian',
        'fi': 'finnish',
        'fr': 'french',
        'de': 'german',
        'el': 'greek',
        'it': 'italian',
        'no': 'norwegian',
        'pl': 'polish',
        'pt': 'portuguese',
        'ru': 'russian',
        'sl': 'slovene',
        'es': 'spanish',
        'sv': 'swedish',
        'tr': 'turkish',
    }
    label_filth_map = {
        'B-ADD': AddressFilth,
        'I-ADD': AddressFilth,
    }

    def __init__(self, dict_vectorizer_json_path: Optional[str] = None,
                 label_encoder_json_path: Optional[str] = None, model_json_path: Optional[str] = None,
                 number_minimum_tokens: int = 5, number_skippable_tokens: int = 2, Start: int = 2, **kwargs):
        super(SklearnDetector, self).__init__(**kwargs)

        # model paths
        self.dict_vectorizer_json_path = dict_vectorizer_json_path
        if self.dict_vectorizer_json_path is None:
            self.dict_vectorizer_json_path = str(pathlib.Path(__file__).parent / 'dict_vectorizer.json')

        self.label_encoder_json_path = label_encoder_json_path
        if self.label_encoder_json_path is None:
            self.label_encoder_json_path = str(pathlib.Path(__file__).parent / 'label_encoder.json')

        self.model_json_path = model_json_path
        if self.model_json_path is None:
            self.model_json_path = str(pathlib.Path(__file__).parent / 'model.json')

        self.n_prev_tokens = 3
        self.n_next_tokens = 5

        self.tokeniser = None  # type: Optional[TokenizerI]
        self.dict_vectorizer = None  # type: Optional[DictVectorizer]
        self.model = None  # type: Optional[LogisticRegression]
        self.label_encoder = None  # type: Optional[LabelEncoder]

        try:
            self.punct_language = self.punct_languages[self.language]
        except KeyError:
            raise ValueError('The locale is not supported by punct and so this detector cannot be used')

    def word_tokenize(self, text: str) -> List[str]:
        if self.tokeniser is None:
            self.tokeniser = nltk.tokenize.destructive.NLTKWordTokenizer()

        sentences = nltk.tokenize.sent_tokenize(text, language=self.punct_language)
        return [
            token for sent in sentences for token in self.tokeniser.tokenize(sent)
        ]

    def word_tokenize_with_positions(self, text: str, document_name: DocumentName) -> List[TokenTuple]:
        tokens = self.word_tokenize(text)
        token_positions = self.token_positions(text, tokens)
        return [
            TokenTuple(doc_name=document_name, token=token, span=position)
            for token, position in zip(tokens, token_positions)
        ]
        # return list(zip([document_name] * len(tokens), tokens, token_positions))

    @staticmethod
    def token_positions(text: str, tokens: Collection[str]) -> List[TokenPosition]:
        if len(tokens) == 0:
            raise ValueError("tokens should not be empty")
        if len(text.strip()) == 0:
            raise ValueError("text should not be empty")

        non_token_pattern = "(?:[^a-zA-Z0-9]*)"
        inter_token_pattern = "){inter}(".format(inter=non_token_pattern)
        start_end_pattern = "^{inter}({tokens}){inter}$"

        # TODO: re.escape(tok) might need replacements
        pattern = start_end_pattern.format(
            tokens=inter_token_pattern.join([re.escape(tok) for tok in tokens]),
            inter=non_token_pattern,
        )

        match = re.match(pattern, text, re.DOTALL)
        if match is None:
            print(text.__repr__())
            print(tokens.__repr__())
            print(pattern.__repr__())
            raise ValueError('Tokens were not able to be matched to original document')
        groups = match.groups()
        n_groups = len(groups)
        if len(tokens) != n_groups or tokens != list(groups):
            print(text.__repr__())
            print(tokens.__repr__())
            print(pattern.__repr__())
            raise ValueError('Matched tokens do not matched the expected tokens')

        return [
            TokenPosition(*match.span(i_group))
            for i_group, token in zip(range(1, n_groups + 1), tokens)
        ]

    @staticmethod
    def create_features_single_token(token: str, prefix: str = '') -> Dict[str, Any]:
        token = token.strip(' \t\r\v\f')
        features = {
            prefix + 'capitalised': token.istitle(),
            prefix + 'lower': token.islower(),
            prefix + 'upper': token.isupper(),
            prefix + 'numeric': token.isdigit(),
            prefix + 'alphanumeric': any(c.isdigit() for c in token) and any(c.isalpha() for c in token),
            prefix + 'length_long': len(token) >= 12,
            prefix + 'length_short': len(token) <= 5,
        }
        return features

    @staticmethod
    def _create_features_with_context(features: Dict[str, Any], prev_features: Collection[Dict[str, Any]],
                                      next_features: Collection[Dict[str, Any]]) -> Dict[str, Any]:
        full_feature_set = copy.copy(features)

        len_prev = len(prev_features)
        for i, feature_items in enumerate(prev_features):
            prefix = "prev_{:#02d}_".format(len_prev - i)
            full_feature_set.update({prefix + k: v for k, v in feature_items.items()})

        for i, feature_items in enumerate(next_features):
            prefix = "next_{:#02d}_".format(i + 1)
            full_feature_set.update({prefix + k: v for k, v in feature_items.items()})

        return full_feature_set

    def create_features(self, token_tuples: Collection[Union[TokenTuple, TokenTupleWithLabel]], n_prev_tokens: int = 3,
                        n_next_tokens: int = 5) -> List[Dict[str, str]]:
        feature_list = [(t[0], self.create_features_single_token(t[1])) for t in token_tuples]
        all_features = []
        for i, (doc_id, token_features) in enumerate(feature_list):
            prev_features = [
                t[1]
                for t in feature_list[i - n_prev_tokens if i - n_prev_tokens >= 0 else 0:i]
                if t[0] == doc_id
            ]
            next_features = [
                t[1]
                for t in feature_list[i + 1:i + 1 + n_next_tokens]
                if t[0] == doc_id
            ]

            all_features.append(
                self._create_features_with_context(token_features, prev_features, next_features)
            )
        return all_features

    def load_model(self) -> None:
        if self.dict_vectorizer is None and self.dict_vectorizer_json_path is not None:
            self.dict_vectorizer = estimator_from_json(self.dict_vectorizer_json_path)

        if self.model is None and self.model_json_path is not None:
            self.model = estimator_from_json(self.model_json_path)

        if self.label_encoder is None and self.label_encoder_json_path is not None:
            self.label_encoder = estimator_from_json(self.label_encoder_json_path)

    def save_model(self) -> None:
        if self.dict_vectorizer is not None and self.dict_vectorizer_json_path is not None:
            estimator_to_json(self.dict_vectorizer, self.dict_vectorizer_json_path)

        if self.model is not None and self.model_json_path is not None:
            estimator_to_json(self.model, self.model_json_path)

        if self.label_encoder is not None and self.label_encoder_json_path is not None:
            estimator_to_json(self.label_encoder, self.label_encoder_json_path)

    @staticmethod
    def _add_labels_to_tokens(token_tuples: Collection[Union[TokenTuple, TokenTupleWithLabel]],
                              labels: Collection[str]) -> List[TokenTupleWithLabel]:
        if len(token_tuples) != len(labels):
            raise ValueError("token_tuples and labels should be of the same length")
        return [
            TokenTupleWithLabel(doc_name=doc_id, token=token, span=position, label=new_label)
            for (doc_id, token, position, *old_label), new_label in zip(token_tuples, labels)
        ]

    def predict(self, document_list: Collection[str],
                document_names: Optional[Collection[DocumentName]] = None) -> List[TokenTupleWithLabel]:
        self.load_model()
        if self.dict_vectorizer is None or self.model is None or self.label_encoder is None:
            raise ValueError("Unable to load serialised model")

        if document_names is None or len(document_names) == 0:
            document_names = list(range(len(document_list)))

        # TODO: delete old code
        # text_tokens = [(0, token, 'NA') for token in self.word_tokenize(text)]
        # text_token_positions = self.token_positions(text=text, tokens=[x[1] for x in text_tokens])
        text_tokens = [
            token_tuple
            for doc_name, text in zip(document_names, document_list)
            for token_tuple in self.word_tokenize_with_positions(text=text, document_name=doc_name)
        ]
        text_features = self.create_features(text_tokens,
                                             n_prev_tokens=self.n_prev_tokens, n_next_tokens=self.n_next_tokens)

        text_data = self.dict_vectorizer.transform(text_features)
        text_prediction = self.model.predict(text_data)
        text_labels = self.label_encoder.inverse_transform(text_prediction)

        return self._add_labels_to_tokens(text_tokens, text_labels)

    @staticmethod
    def _get_label(filth: Filth, prev_label: Optional[str] = None) -> str:
        """Returns the name of the label based on the filth type"""
        if isinstance(filth, KnownFilth) and filth.comparison_type is not None:
            return filth.comparison_type.upper()
        elif filth.type not in (None, 'known'):
            return filth.type.upper()
        raise ValueError(f'Unable to determine label to assign to filth: f{filth}')

    @staticmethod
    def _add_labels_to_tokens_using_known_filth(
            token_tuples: Collection[Union[TokenTuple, TokenTupleWithLabel]], known_filth_items: Collection[KnownFilth]
    ) -> List[TokenTupleWithLabel]:
        new_token_tuples = []  # type: List[TokenTupleWithLabel]
        current_doc_name = None  # type: Optional[Union[str, int]]
        current_doc_known_items = None  # type: Optional[List[KnownFilth]]

        for i_token, (doc_name, token, (token_start, token_end), *additional_vars) in enumerate(token_tuples):

            if current_doc_name is None or current_doc_known_items is None or current_doc_name != doc_name:
                current_doc_name = doc_name
                current_doc_known_items = [ki for ki in known_filth_items if ki.document_name == current_doc_name]

            matching_known_items = [
                ki for ki in current_doc_known_items
                # TODO: tests around these equalities
                if ki.end >= token_start and ki.beg < token_end
            ]
            new_label = additional_vars[0] if len(additional_vars) > 0 else 'O'
            if len(matching_known_items) > 0:
                try:
                    prev_label = new_token_tuples[-1][3]  # type: Optional[str]
                except IndexError:
                    prev_label = None
                new_label = SklearnDetector._get_label(matching_known_items[0], prev_label)
                if len(matching_known_items) > 1:
                    multi_types = [ki.comparison_type for ki in known_filth_items].__repr__()
                    warnings.warn(f"Token '{token}' in '{doc_name}' has been labelled as multiple types of filth: "
                                  f"{multi_types}")
            new_token_tuples.append(
                TokenTupleWithLabel(
                    doc_name=doc_name, token=token, span=TokenPosition(token_start, token_end), label=new_label
                )
            )

        return new_token_tuples

    def train(self, document_list: Collection[str], known_filth_items: Collection[KnownFilth],
              document_names: Optional[Collection[DocumentName]] = None, dict_vectorizer_kwargs: Optional[Dict] = None,
              logistic_regression_kwargs: Optional[Dict] = None) -> List[TokenTupleWithLabel]:

        if len(document_list) == 0:
            raise ValueError('Must pass some documnts to train on')

        if document_names is None or len(document_names) != len(document_list):
            document_names = [x for x in range(len(document_list))]

        self.dict_vectorizer = DictVectorizer(**(dict_vectorizer_kwargs if dict_vectorizer_kwargs else {}))
        self.model = LogisticRegression(**(logistic_regression_kwargs if logistic_regression_kwargs else {}))
        self.label_encoder = LabelEncoder()

        print('tokens')
        text_tokens = [
            token_tuple
            for doc_name, text in zip(document_names, document_list)
            for token_tuple in self.word_tokenize_with_positions(text=text, document_name=doc_name)
        ]
        text_tokens_with_labels = self._add_labels_to_tokens_using_known_filth(text_tokens, known_filth_items)
        del text_tokens

        print('features')
        text_features = self.create_features(text_tokens_with_labels,
                                             n_prev_tokens=self.n_prev_tokens, n_next_tokens=self.n_next_tokens)

        print('sklearn')
        target = self.label_encoder.fit_transform([x[3] for x in text_tokens_with_labels])
        text_data = self.dict_vectorizer.fit_transform(text_features)
        self.model = self.model.fit(text_data, target)
        text_prediction = self.model.predict(text_data)
        text_labels = self.label_encoder.inverse_transform(text_prediction)

        print('finishing')
        # TODO: return both predited and true labels
        text_tokens_with_labels = self._add_labels_to_tokens(text_tokens_with_labels, text_labels)

        print('done')
        return text_tokens_with_labels

    def _yield_filth(self, text: str, token_tuple_list: Collection[TokenTupleWithLabel],
                     document_name: Optional[DocumentName] = None) -> Generator[Filth, None, None]:
        for i_token, (doc_name, token, span, *additional_vars) in enumerate(token_tuple_list):
            if len(additional_vars) < 1:
                raise ValueError('A token is not labelled, cannot yield Filth.')
            label = additional_vars[0]
            if label in self.label_filth_map:
                filth_cls = self.label_filth_map[label]
                yield filth_cls(
                        beg=span[0],
                        end=span[1],
                        text=text[span[0]:span[1]],
                        document_name=(str(document_name) if document_name else None),  # None if no doc_name provided
                        detector_name=self.name,
                        locale=self.locale,
                )

    # TODO: add support for the multi doc iter_filth too
    def iter_filth(self, text: str, document_name: Optional[DocumentName] = None) -> Generator[Filth, None, None]:
        token_tuple_list = self.predict(text)
        yield from self._yield_filth(text, token_tuple_list, document_name=document_name)

    @classmethod
    def supported_locale(cls, locale: str) -> bool:
        """Returns true if this ``Detector`` supports the given locale.

        :param locale: The locale of the documents in the format: 2 letter lower-case language code followed by an
                       underscore and the two letter upper-case country code, eg "en_GB" or "de_CH".
        :type locale: str
        :return: ``True`` if the locale is supported, otherwise ``False``
        :rtype: bool
        """
        language, region = cls.locale_split(locale)
        return language in cls.punct_languages.keys()


class BIOTokenSklearnDetector(SklearnDetector):
    name = "bio_token_sklearn"
    label_filth_map = {
        'ADD': AddressFilth,
    }

    def __init__(self, minimum_ntokens: int = 5, maximum_token_distance: int = 4, b_token_required: bool = True,
                 **kwargs):
        super(BIOTokenSklearnDetector, self).__init__(**kwargs)
        self.minimum_ntokens = minimum_ntokens
        self.maximum_token_distance = maximum_token_distance
        self.b_token_required = b_token_required

    @staticmethod
    def remove_iob_from_label(label: str) -> str:
        parts = label.split('-')
        if parts[0] in ('B', 'I'):
            return '-'.join(parts[1:])
        return label

    @staticmethod
    def get_iob_from_label(label: str) -> str:
        parts = label.split('-')
        if parts[0] in ('B', 'I'):
            return parts[0].upper()
        return label

    @staticmethod
    def _get_label(filth: Filth, prev_label: Optional[str] = None) -> str:
        if isinstance(filth, KnownFilth) and filth.comparison_type is not None:
            new_label = filth.comparison_type.upper()
        elif hasattr(filth, 'type') and filth.type not in (None, 'known'):
            new_label = filth.type.upper()
        else:
            raise ValueError(f'Unable to determine label to assign to filth: f{filth}')

        if prev_label in ("B-" + new_label, "I-" + new_label):
            new_label = "I-" + new_label
        else:
            new_label = "B-" + new_label
        return new_label

    @staticmethod
    def _combine_iob_tokens(
        text: str, text_tokens: Collection[TokenTupleWithLabel], minimum_ntokens: int,
        maximum_token_distance: int, b_token_required: bool
    ) -> List[TokenTupleWithLabel]:
        """Combines The B-XXX and I-XXX tags into single objects that are labelled simply as XXX."""
        # TODO: maximum_token_distance should be in tokens not chars
        final_tokens = []

        combined_filth_location = None  # type: Optional[TokenPosition]
        combined_filth_label = None  # type: Optional[str]
        combined_filth_ntokens = 0

        for token in text_tokens:
            if BIOTokenSklearnDetector.get_iob_from_label(token.label) == 'O':
                continue

            print((token.span.beg, token.span.end), token.label)

            if combined_filth_location is not None and combined_filth_label is not None:
                max_start_position = combined_filth_location[1] + maximum_token_distance
                if token.span.beg <= max_start_position \
                        and BIOTokenSklearnDetector.remove_iob_from_label(token.label) == combined_filth_label:
                    # Extend existing filth
                    # print('combine...')
                    combined_filth_location = TokenPosition(
                        min([combined_filth_location.beg, token.span.beg]),
                        max([combined_filth_location.end, token.span.end]),
                    )
                    combined_filth_ntokens += 1
                    continue

            if combined_filth_ntokens >= minimum_ntokens and combined_filth_location is not None:
                # Issue the collected new filth
                # print('ISSUE')
                final_tokens.append(
                    TokenTupleWithLabel(
                        doc_name=token.doc_name,
                        token=text[combined_filth_location.beg:combined_filth_location.end],
                        span=combined_filth_location,
                        label=combined_filth_label if combined_filth_label is not None else token.label,
                    )
                )

            # Reset
            # print('Reset')
            combined_filth_location = None
            combined_filth_label = None
            combined_filth_ntokens = 0

            if b_token_required and not token.label.startswith('B-'):
                continue

            # Start collecting a new filth
            combined_filth_location = TokenPosition(token.span.beg, token.span.end)
            combined_filth_label = BIOTokenSklearnDetector.remove_iob_from_label(token.label)
            combined_filth_ntokens = 1

        if combined_filth_ntokens >= minimum_ntokens and combined_filth_location is not None:
            # Issue the collected new filth
            # print('ISSUE')
            final_tokens.append(
                TokenTupleWithLabel(
                    doc_name=token.doc_name,
                    token=text[combined_filth_location.beg:combined_filth_location.end],
                    span=combined_filth_location,
                    label=combined_filth_label if combined_filth_label is not None else token.label,
                )
            )

        return final_tokens

    def iter_filth(self, text, document_name: Optional[DocumentName] = None) -> Generator[Filth, None, None]:
        text_tokens = self.predict(text)
        print(pd.Series([x.label for x in text_tokens]).value_counts())
        text_tokens = self._combine_iob_tokens(
            text=text,
            text_tokens=text_tokens,
            minimum_ntokens=self.minimum_ntokens,
            maximum_token_distance=self.maximum_token_distance,
            b_token_required=self.b_token_required,
        )
        yield from self._yield_filth(text, token_tuple_list=text_tokens, document_name=document_name)
