import re

from llmhub_lib.model_extractor.utils import find_quantization, get_model_data_from_file_name


class GenericModelExtractor:
    def __init__(self, file_path):
        self.file_path = file_path
        self.data = self.get_model_data()


    def get_repo_uri(self):
        return self.data.get('source') + '/' + self.data.get('creator') + '/' + self.data.get('model_name') + '/' + self.data.get('version') + '/' + self.data.get('quantization')


    def get_model_data(self):
        return get_model_data_from_file_name(self.file_path)

