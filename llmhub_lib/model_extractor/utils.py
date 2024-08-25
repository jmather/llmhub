import re

SEPARATOR_CHARACTERS = ['-', '.']
SEPARATOR_PATTERN = '|'.join([ re.escape(c) for c in SEPARATOR_CHARACTERS ])


def find_quantization(file_name):
    # We split by "." or "-" to get the parts of the file name
    file_name_parts = re.split(rf'[-.]' , file_name)
    print(f"[utils.find_quantization] File name: {file_name}")
    print(f"[utils.find_quantization] File name parts: {file_name_parts}")
    # second to last part is the quantization, if it exists
    quantization = None
    if len(file_name_parts) > 2:
        quantization_part = file_name_parts[-2]
        if quantization_part.startswith('Q') or quantization_part.startswith('quantized') or quantization_part == 'f16':
            quantization = quantization_part

    return quantization


def find_version(string):
    # Find the v#+(.#+)? pattern at the end of the model name
    version = None
    version_match = re.search(r'v\d+(\.\d+)?(\.\d+)?(\.\d+)?', string)
    patch_match = re.search(r'patch\d+$', string)
    if version_match:
        version = version_match.group()
    # I've also seen it in patch## format, like 'patch17', at the end of the string
    elif patch_match:
        version = patch_match.group()

    return version


def massage_model_name(model_name, version, quantization):
    print(f"[ModelNameTrim] Model name: {model_name}, version: {version}, quantization: {quantization}")
    # If we have a version, we want to remove it from the model name
    if version:
        # We should match on something like "SEPARATOR_PATTERN{version}(SEPARATOR_PATTERN)" so we can replace with the second separator
        esc_version = re.escape(version)
        model_name = re.sub(rf'[-._]?{esc_version}', '', model_name)

    # If we have a quantization, we want to remove it from the model name
    if quantization:
        esc_quantization = re.escape(quantization)
        model_name = re.sub(rf'[-._]?{esc_quantization}', '', model_name)

    print(f"[ModelNameTrim] Massaged model name: {model_name}")
    return model_name

def get_model_data_from_file_name(file_path):
    # however this is a full file path, probably to something like...
    # /Users/user/.cache/huggingface/hub/blah... or /Users/user/.cache/lm-studio/models/blah...
    path_parts = file_path.split('/')

    # So likely, we want the fragment BEFORE the fragement before the fragment that has the creator name for source
    source = path_parts[-5]
    creator_name = path_parts[-3]
    model_name = path_parts[-2]
    model_file = path_parts[-1]

    # let's see if model_name ends with a version like string
    # Find the v#+(.#+)? pattern at the end of the model name
    version = find_version(model_name)

    # Now we look at the file name to see if it's a quantized model
    # We look at the second to last segment in the file name, and we check for the Q# pattern
    quantization = find_quantization(file_path)

    return {
        'source': source,
        'creator': creator_name,
        'model_name': massage_model_name(model_name, version, quantization),
        'version': version,
        'quantization': quantization,
        'path': file_path
    }

