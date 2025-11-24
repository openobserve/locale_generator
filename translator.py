import json
import boto3
import os

translate = boto3.client('translate')

def CreateTranslationFile(locale, generation_type="all"):
    targetOutput = convertLocaleTo(locale, generation_type)

    f = open("output/" + locale + ".json", "w")
    f.write(json.dumps(targetOutput, indent=2, ensure_ascii=False))
    f.close()

    print(f"Translation file created: {locale}.json (generation_type: {generation_type})")

def convertLocaleTo(locale, generation_type="all"):
    newLocale = {}
    existingLocale = {}

    # Load existing translation file if it exists and generation_type is "delta"
    output_file_path = f"output/{locale}.json"
    if generation_type == "delta" and os.path.exists(output_file_path):
        with open(output_file_path) as f:
            existingLocale = json.load(f)
            newLocale = existingLocale.copy()

    with open('en_gb.json') as f:
        data = json.load(f)
        for section in data:
            if section not in newLocale:
                newLocale[section] = {}

            for key in data[section]:
                # For delta mode, only translate if the key doesn't exist in the existing translation
                if generation_type == "delta" and section in existingLocale and key in existingLocale[section]:
                    # Skip translation, key already exists
                    continue

                # Translate the text
                translatedText = translate.translate_text(
                    Text=data[section][key],
                    SourceLanguageCode='en',
                    TargetLanguageCode=locale
                )
                newLocale[section][key] = translatedText['TranslatedText']

    return newLocale
