import json
import boto3
import os
from botocore.exceptions import NoCredentialsError

translate = boto3.client('translate')

def CreateTranslationFile(locale):
    targetOutput = convertLocaleTo(locale)

    f = open("../zinc-cp-cloud-ui/src/locales/languages/" + locale + ".json", "w")
    f.write(json.dumps(targetOutput, indent=2, ensure_ascii=False))
    f.close()

    print("Translation file created: ", locale + ".json")


def CreateOpenSourceTranslationFile(locale):
    # Convert en.json to target language dictionary, removing already translated items
    targetOutput = convertLocaleTo(locale)

    # Define the path for the target language file (e.g., fr.json, es.json)
    target_file_path = f"../openobserve/web/src/locales/languages/{locale}.json"

    # Check if the target language file exists
    if os.path.exists(target_file_path):
        # If it exists, load the current translations
        with open(target_file_path, "r", encoding="utf-8") as f:
            existing_translations = json.load(f)
        # Merge the existing translations with the new ones, skipping translation for existing values
        merged_translations = merge_translations(existing_translations, targetOutput)
    else:
        # If the file doesn't exist, use the new translations
        merged_translations = targetOutput

    # Write the merged translations back to the target file
    with open(target_file_path, "w", encoding="utf-8") as f:
        f.write(json.dumps(merged_translations, indent=2, ensure_ascii=False))

    print(f"Translation file created/updated: {locale}.json")


def convertLocaleTo(locale):
    newLocale = {}

    # Load the source (English) JSON file
    with open('../openobserve/web/src/locales/languages/en.json', encoding="utf-8") as f:
        data = json.load(f)

    target_file_path = f"../openobserve/web/src/locales/languages/{locale}.json"

    # Load existing target language translations (if the file exists)
    if os.path.exists(target_file_path):
        with open(target_file_path, "r", encoding="utf-8") as f:
            existing_translations = json.load(f)
    else:
        existing_translations = {}

    for section in data:
        newLocale[section] = translate_nested_object(
            data[section],
            existing_translations.get(section, {}),
            locale
        )

    return newLocale


def translate_nested_object(source_obj, existing_obj, locale):
    """
    Recursively translates nested objects.
    If a value is a string, translate it.
    If a value is a dict, recurse into it.
    """
    result = {}

    for key, value in source_obj.items():
        # Check if this key exists in existing translations
        if key in existing_obj:
            if isinstance(value, dict) and isinstance(existing_obj[key], dict):
                # Both are dicts, recurse to check for new nested keys
                result[key] = translate_nested_object(value, existing_obj[key], locale)
            else:
                # Key exists, keep the existing translation
                result[key] = existing_obj[key]
        else:
            # Key doesn't exist, need to translate
            if isinstance(value, dict):
                # It's a nested object, recurse
                result[key] = translate_nested_object(value, {}, locale)
            else:
                # It's a string, translate it
                result[key] = translate_text(value, locale)

    return result


def translate_text(text, locale):
    # Example: Translate using any external service, handle exceptions if needed
    try:
        translatedText = translate.translate_text(
            Text=text,
            SourceLanguageCode='en',
            TargetLanguageCode=locale
        )
        return translatedText['TranslatedText']
    except NoCredentialsError:
        print("No credentials for the translation service.")
        return text  # Fallback to the original text in case of an error


def merge_translations(existing_translations, new_translations):
    """
    Merges the existing translations with new translations.
    If a translation already exists, it skips translation.
    """
    for section, keys in new_translations.items():
        if section not in existing_translations:
            # If section doesn't exist, add it entirely
            existing_translations[section] = keys
        else:
            for key, value in keys.items():
                # Only add keys that don't already exist
                if key not in existing_translations[section]:
                    existing_translations[section][key] = value
    return existing_translations