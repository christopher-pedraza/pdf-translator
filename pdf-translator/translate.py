
from googletrans import Translator

translator = Translator()
r = translator.translate('An acute accent marks the vowel of a stressed syllable.', dest='es', src='en')
print(r.text)
