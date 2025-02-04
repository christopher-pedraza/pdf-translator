from pdf2image import convert_from_path
import pytesseract
from googletrans import Translator
from PyPDF2 import PdfWriter
from reportlab.pdfgen import canvas
from PIL import Image, ImageDraw, ImageFont
import io

# Specify the path to the Poppler bin directory
poppler_path = r"poppler\\Library\bin"  # Relative path to the Poppler bin folder

# Function to perform OCR and get bounding box information
def ocr_with_bounding_boxes(image):
    data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
    return data

# Function to translate text
def translate_text(text, src_language='en', dest_language='es'):
    print("\n\n\nTranslating text:", text)
    print("\n\n\n")
    translator = Translator()

    translated = []
    for t in text:
        print(f"\t\t{t}->", end='')
        if t == '':
            print('')
            translated.append('')
        else:
            try:
                translated_word = translator.translate(t, dest=dest_language, src=src_language)
                translated.append(translated_word.text)
                print(f"{translated_word.text}")
            except Exception:
                translated.append(t)
                print(f"{t}")

    # translated = translator.translate(text, dest=dest_language, src=src_language)
    print("\n\n\nTranslated text:", translated)
    print("\n\n\n")
    return translated

# Function to overlay translated text with dynamic font resizing and text wrapping
def overlay_translated_text(image, ocr_data, translated_texts):
    draw = ImageDraw.Draw(image)
    
    # Default font size and maximum number of lines for wrapping
    max_font_size = 12  # Start with the largest font size
    min_font_size = 6   # Minimum font size to avoid unreadable text
    max_lines = 3       # Maximum number of lines for text wrapping
    
    for i in range(len(ocr_data["text"])):
        if ocr_data["text"][i].strip():  # Only process non-empty text
            x = ocr_data["left"][i]
            y = ocr_data["top"][i]
            w = ocr_data["width"][i]
            h = ocr_data["height"][i]
            
            # Get the translated text for this word/line
            translated_text = translated_texts[i]
            
            # Try different font sizes until the text fits within the bounding box
            font_size = max_font_size
            font = None
            text_width = float('inf')
            
            while font_size >= min_font_size:
                try:
                    font = ImageFont.truetype("arial.ttf", size=font_size)
                except IOError:
                    font = ImageFont.load_default()
                
                # Measure the width and height of the text using font.getbbox()
                bbox = font.getbbox(translated_text)
                text_width = bbox[2] - bbox[0]  # Width = right - left
                text_height = bbox[3] - bbox[1]  # Height = bottom - top
                
                # Check if the text fits within the bounding box
                if text_width <= w:
                    break
                
                # Reduce the font size if the text doesn't fit
                font_size -= 1
            
            # If the text still doesn't fit, wrap it into multiple lines
            if text_width > w:
                lines = []
                words = translated_text.split(' ')
                current_line = ''
                
                for word in words:
                    # Check if adding the next word exceeds the width
                    test_line = current_line + word + ' '
                    test_bbox = font.getbbox(test_line)
                    test_width = test_bbox[2] - test_bbox[0]
                    
                    if test_width <= w:
                        current_line = test_line
                    else:
                        lines.append(current_line.strip())
                        current_line = word + ' '
                
                # Add the last line
                lines.append(current_line.strip())
                
                # Limit the number of lines
                if len(lines) > max_lines:
                    lines = lines[:max_lines]
                    lines[-1] = lines[-1][:len(lines[-1]) - 3] + '...'  # Add ellipsis if truncated
                
                # Draw each line
                for j, line in enumerate(lines):
                    draw.text((x, y + j * text_height), line, fill="black", font=font)
            else:
                # Draw the single-line text
                draw.text((x, y), translated_text, fill="black", font=font)

# Main function to process the PDF
def process_pdf(input_pdf_path, output_pdf_path, dest_language='en'):
    # Convert PDF to images
    images = convert_from_path(input_pdf_path, poppler_path=poppler_path)
    
    translated_images = []

    for i, image in enumerate(images):
        print(f"Processing page {i + 1}")
        
        # Perform OCR and get bounding box information
        ocr_data = ocr_with_bounding_boxes(image)

        # print("ocr_data:", ocr_data["text"])

        texts_list = ocr_data["text"]
        # translated_texts = translate_text(texts_list, dest_language='es', src_language='en')
        translated_texts = ['', '', '', '', ' ', '', '', '', ' ', '', '', '', 'Dramatis', 'persona', '', '', '', 'a', 'cute', 'acento', 'marcas', 'the', 'vocal', 'de', 'a', 'stressed', 'sílaba.', 'Dónde', 'semejante', 'a', 'vocal', '', 'todos', 'en', 'un', 'open', 'sílaba', 'él', 'voluntad', 'a menudo', 'ser', 'long', '(p.ej.,', 'Humbaaba).', 'En', 'some', '', 'nombres', 'the', 'posición', 'de', 'the', 'estrés', 'es', 'conjetural.', '', '', '', 'Gilgamesh,', 'rey', 'de', 'the', 'estado urbano', 'de', 'Uruk', '', 'Ninsun,', 'a', 'diosa,', 'su', 'madre', '', '', 'Enkidu,', 'su', 'friend', 'y', 'companion', '', '', 'Shamhat,', 'a', 'prostitute', 'de', 'Uruk', '', '', 'Shamash,', 'the', 'Sol', 'Dios', '', '', 'Humbaba,', 'the', 'guardian', 'de', 'the', 'Bosque', 'de', 'Cedro', '', 'Ishtar,', 'the', 'principal', 'diosa', 'de', 'Uruk', '', '', 'Shiduri,', 'a', 'menor', 'diosa', 'de', 'sabiduría', '', 'Ur-shanabi,', 'the', 'ferryman', 'de', 'Uta-Napishti', '', 'Uta-Napishti,', 'sobreviviente', 'de', 'the', 'Inundación', '', '', '', 'ACO', 'sentar', 'lis', '', 'mprchensivo', 'lista', 'de', 'the', 'proper', 'sustantivos', 'that', 'ocurrir', 'en', 'the', 'textos', 'translated', '', 'en', 'this', 'libro', 'es', 'given', 'en', 'páginas.', '222ff.', '', '', '', 'a', '', '', '', 'The', 'Estándar', 'Versión', 'de', '', 'the', 'Babylonian', 'Gilgamesh', 'Epic:', '', "'Él", 'OMS', 'sierra', 'the', 'Deep’', '', '', '', 'Tableta', '1.', 'The', 'Coming', 'de', 'Enkidu', '', '', '', 'Prólogo', 'y', 'himno de alegría.', 'Rey', 'Gilgamesh', 'tiranizar', 'the', 'gente', 'de', 'Uruk,', 'OMS', 'quejarse', '', 'a', 'the', 'gallinero.', 'A', 'desviar', 'su', 'superhuman', 'energías', 'the', 'gods', 'crear', 'su', 'contrapartida,', '', 'the', 'salvaje', 'hombre', 'Enkidu,', 'OMS', 'es', 'trajo', 'arriba', 'por', 'the', 'animales', 'de', 'the', 'salvaje.', 'Enkidu', 'es', '', 'manchado', 'por', 'a', 'trapper,', 'OMS', 'desechos', 'a él', 'lejos', 'de', 'the', 'rebaño', 'con', 'a', 'prostitute.', 'The', '', 'prostitute', 'espectáculos', 'a él', 'su', 'letras', 'y', 'proponerse', 'a', 'llevar', 'a él', 'a', 'Uruk,', 'dónde', 'Gilgamesh', '', '', '', 'tiene', 'estado', 'vidente', 'a él', 'en', 'sueños.', '', '', '', 'Él', 'OMS', 'sierra', 'the', 'Deep,', 'the', 'del país', 'base,', '', '{OMS]', 'sabía...', ',', 'era', 'wise', 'en', 'all', '¡asuntos!', '', '', '[Gilgamesh,', 'OMS]', 'sierra', 'the', 'Deep,', 'the', 'del país', 'base', '', '{OMS]', 'sabía', '...', 'era', 'wise', 'en', 'all', '¡asuntos!', '', '', '', '{Él]', '...', 'en todos lados...', '', 'y', '[aprendió]', 'de', 'everything', 'the', 'suma', 'de', 'sabiduría.', '', '', 'Él', 'sierra', 'qué', 'era', 'secret,', 'discovered', 'qué', 'era', 'hidden,', '', 'él', 'trajo', 'atrás', 'a', 'cuento', 'de', 'antes', 'the', 'Diluvio.', '', '', '', 'Él', 'vino', 'a', 'lejos', 'camino,', 'era', 'weary,', 'encontró', 'paz,', '', '', 'y', 'colocar', 'all', 'su', 'labores', 'en', 'a', 'tableta', 'de', 'piedra.', 'I', '10', '', 'Él', 'built', 'the', 'muralla', 'de', 'Uruk-the-sheepfold,', '', '', 'de', 'holy', 'Eanna,', 'the', 'sacred', 'almacén.', '', '', '', 'Ver', 'es', 'muro', 'como', 'a', 'hebra', 'de', 'lana,', '', 'vista', 'es', 'parapeto', 'that', 'none', 'podría', '¡Copiar!', '', '', 'Llevar', 'the', 'escalera', 'de', 'a', 'bygone', 'era,', 'lis', '', 'dibujar', 'cerca', 'a', 'Eanna,', 'asiento', 'de', 'Ishtar', 'the', 'diosa,', '', '', 'that', 'No', 'más tarde', 'rey', 'podría', 'alguna vez', '¡Copiar!', '', '', '', '']
        
        # Translate each piece of text
        # translated_texts = [translate_text(text, dest_language) for text in ocr_data["text"]]
        
        # Overlay the translated text on the image
        overlay_translated_text(image, ocr_data, translated_texts)
        
        # Append the modified image to the list
        translated_images.append(image)
    
    # Save the translated images as a new PDF
    translated_images[0].save(output_pdf_path, save_all=True, append_images=translated_images[1:])

input_pdf_path = 'sample_s.pdf'
output_pdf_path = 'translated_document.pdf'
process_pdf(input_pdf_path, output_pdf_path, dest_language='es')  # Translate to Spanish