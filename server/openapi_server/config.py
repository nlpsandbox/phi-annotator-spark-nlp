import os
from enum import Enum

defaultValues = {
    "CONFIG_NAME": "",
    "SPARK_JSL_VERSION": "3.1.1",
    "SPARK_NLP_LICENSE": "",
    "EMBEDDINGS_MODEL": "",
    "NER_MODEL": ""
}


class ConfigName(Enum):
    NER_DEID_LARGE = "ner-deid-large"
    NER_DEID_SYNTHETIC = "ner-deid-synthetic"
    NER_DEIDENTIFY_DL = "ner-deidentify-dl"


class AbstractConfig(object):
    """
    Parent class containing get_property to return the environment variable or
    default value if not found.
    """
    def __init__(self):
        self._defaultValues = defaultValues

    def get_property(self, property_name):
        if os.getenv(property_name) is not None:
            return os.getenv(property_name)
        # we don't want KeyError?
        if property_name not in self._defaultValues.keys():
            return None  # No default value found
        # return default value
        return self._defaultValues[property_name]


class Config(AbstractConfig):
    """
    This class is used to provide coniguration values to the application, first
    using environment variables and if not found, defaulting to those values
    provided in the defaultValues dictionary above.
    """

    @property
    def config_name(self):
        return self.get_property('CONFIG_NAME')

    @property
    def spark_jsl_version(self):
        return self.get_property('SPARK_JSL_VERSION')

    @property
    def spark_nlp_license(self):
        return self.get_property('SPARK_NLP_LICENSE')

    @property
    def embeddings_model(self):
        return self.get_property('EMBEDDINGS_MODEL')

    @property
    def ner_model(self):
        return self.get_property('NER_MODEL')


config = Config()
