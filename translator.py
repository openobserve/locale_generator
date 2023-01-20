import json
import boto3

translate = boto3.client('translate')

def CreateTranslationFile(locale):
    targetOutput = convertLocaleTo(locale)

    f = open("output/" + locale + ".json", "w")
    f.write(json.dumps(targetOutput, indent=2, ensure_ascii=False))
    f.close()

    print("Translation file created: ", locale + ".json")

def convertLocaleTo(locale):
    newLocale = {}

    with open('en_gb.json') as f: # 
        data = json.load(f)
        for section in data:
            newLocale[section] = {}
            for key in data[section]:
                translatedText = translate.translate_text(
                    Text=data[section][key],
                    SourceLanguageCode='en',
                    TargetLanguageCode=locale
                )
                newLocale[section][key] = translatedText['TranslatedText']

    return newLocale
