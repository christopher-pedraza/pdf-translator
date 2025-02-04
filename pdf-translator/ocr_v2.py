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
    
    # Extract text and bounding box information
    texts = data["text"]
    lefts = data["left"]
    tops = data["top"]
    widths = data["width"]
    heights = data["height"]

    # Group words into sentences
    sentences = []
    current_sentence = ""
    current_bbox = None

    for i, text in enumerate(texts):
        if text.strip():  # Skip empty strings
            if current_sentence:
                current_sentence += " " + text
            else:
                current_sentence = text
                current_bbox = {
                    "left": lefts[i],
                    "top": tops[i],
                    "width": widths[i],
                    "height": heights[i],
                }

            # Check if the current word ends with a punctuation mark
            if any(char in ".!?:" for char in text):
                sentences.append((current_sentence, current_bbox))
                current_sentence = ""
                current_bbox = None

    # Add any remaining text as a sentence (in case there's no punctuation at the end)
    if current_sentence:
        sentences.append((current_sentence, current_bbox))

    return sentences

# Function to translate text
def translate_text(sentences, src_language='en', dest_language='es'):
    print("\n\n\nTranslating sentences:", [s[0] for s in sentences])
    print("\n\n\n")
    translator = Translator()
    translated_sentences = []

    for sentence, bbox in sentences:
        print(f"\t\t{sentence}->", end='')
        if not sentence.strip():
            print('')
            translated_sentences.append(("", bbox))
        else:
            try:
                translated_sentence = translator.translate(sentence, dest=dest_language, src=src_language)
                translated_sentences.append((translated_sentence.text, bbox))
                print(f"{translated_sentence.text}")
            except Exception as e:
                print(f"Translation failed for sentence: '{sentence}'. Error: {e}")
                translated_sentences.append((sentence, bbox))
                print(f"{sentence}")

    print("\n\n\nTranslated sentences:", [s[0] for s in translated_sentences])
    print("\n\n\n")
    return translated_sentences

# Function to overlay translated text with dynamic font resizing and text wrapping
def overlay_translated_text(image, sentences):
    draw = ImageDraw.Draw(image)

    # Default font size and maximum number of lines for wrapping
    max_font_size = 12  # Start with the largest font size
    min_font_size = 6   # Minimum font size to avoid unreadable text
    max_lines = 3       # Maximum number of lines for text wrapping

    for sentence, bbox in sentences:
        if sentence.strip():  # Only process non-empty sentences
            x = bbox["left"]
            y = bbox["top"]
            w = bbox["width"]
            h = bbox["height"]

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
                bbox_text = font.getbbox(sentence)
                text_width = bbox_text[2] - bbox_text[0]  # Width = right - left
                text_height = bbox_text[3] - bbox_text[1]  # Height = bottom - top

                # Check if the text fits within the bounding box
                if text_width <= w:
                    break

                # Reduce the font size if the text doesn't fit
                font_size -= 1

            # If the text still doesn't fit, wrap it into multiple lines
            if text_width > w:
                lines = []
                words = sentence.split(' ')
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
                draw.text((x, y), sentence, fill="black", font=font)

# Main function to process the PDF
def process_pdf(input_pdf_path, output_pdf_path, dest_language='en'):
    # Convert PDF to images
    images = convert_from_path(input_pdf_path, poppler_path=poppler_path)

    translated_images = []

    for i, image in enumerate(images):
        print(f"Processing page {i + 1}")

        # Perform OCR and get sentences with bounding box information
        sentences = ocr_with_bounding_boxes(image)

        # Translate sentences
        translated_sentences = translate_text(sentences, dest_language=dest_language)

        # Overlay the translated sentences on the image
        overlay_translated_text(image, translated_sentences)

        # Append the modified image to the list
        translated_images.append(image)

    # Save the translated images as a new PDF
    translated_images[0].save(output_pdf_path, save_all=True, append_images=translated_images[1:])
    
input_pdf_path = 'sample_s.pdf'
output_pdf_path = 'translated_document.pdf'
process_pdf(input_pdf_path, output_pdf_path, dest_language='es')  # Translate to Spanish