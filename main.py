import json
from translator import CreateTranslationFile

# Get the list of languages at - https://docs.aws.amazon.com/translate/latest/dg/what-is-languages.html

# Load configuration from config.json
with open('config.json') as config_file:
    config = json.load(config_file)

# Process each language from the config
for lang_config in config['languages']:
    locale = lang_config['code']
    generation_type = lang_config.get('generation_type', 'all')  # Default to 'all' if not specified

    print(f"Processing {locale} with generation_type: {generation_type}")
    CreateTranslationFile(locale, generation_type)
