from .generic_model_extractor import GenericModelExtractor
from .huggingface_model_extractor import HuggingfaceModelExtractor


def extract_model(file_path):
    if 'huggingface' in file_path:
        return HuggingfaceModelExtractor(file_path).data
    return GenericModelExtractor(file_path).data