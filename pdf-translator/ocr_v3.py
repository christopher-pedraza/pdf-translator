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
            # Update the current sentence
            if current_sentence:
                current_sentence += " " + text
            else:
                current_sentence = text

            # Calculate the bounding box for the current word
            word_bbox = {
                "left": lefts[i],
                "top": tops[i],
                "right": lefts[i] + widths[i],
                "bottom": tops[i] + heights[i],
            }

            # Update the sentence bounding box
            if current_bbox is None:
                current_bbox = word_bbox
            else:
                # Expand the sentence bounding box to include the current word
                current_bbox["left"] = min(current_bbox["left"], word_bbox["left"])
                current_bbox["top"] = min(current_bbox["top"], word_bbox["top"])
                current_bbox["right"] = max(current_bbox["right"], word_bbox["right"])
                current_bbox["bottom"] = max(current_bbox["bottom"], word_bbox["bottom"])

            # Check if the current word ends with a punctuation mark
            if any(char in ".!?:" for char in text):
                # Convert bbox to width/height format
                sentence_bbox = {
                    "left": current_bbox["left"],
                    "top": current_bbox["top"],
                    "width": current_bbox["right"] - current_bbox["left"],
                    "height": current_bbox["bottom"] - current_bbox["top"],
                }
                sentences.append((current_sentence, sentence_bbox))
                current_sentence = ""
                current_bbox = None

    # Add any remaining text as a sentence (in case there's no punctuation at the end)
    if current_sentence:
        sentence_bbox = {
            "left": current_bbox["left"],
            "top": current_bbox["top"],
            "width": current_bbox["right"] - current_bbox["left"],
            "height": current_bbox["bottom"] - current_bbox["top"],
        }
        sentences.append((current_sentence, sentence_bbox))

    return sentences

def debug_draw_bounding_boxes(image, sentences):
    draw = ImageDraw.Draw(image)
    for _, bbox in sentences:
        x = bbox["left"]
        y = bbox["top"]
        w = bbox["width"]
        h = bbox["height"]
        draw.rectangle([x, y, x + w, y + h], outline="red", fill="white", width=2)

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
    debug_draw_bounding_boxes(image, sentences)

    # Default maximum and minimum font sizes
    max_font_size = 200  # Start with a large font size
    min_font_size = 6    # Minimum font size to avoid unreadable text

    for sentence, bbox in sentences:
        if sentence.strip():  # Only process non-empty sentences
            x = bbox["left"]
            y = bbox["top"]
            w = bbox["width"]
            h = bbox["height"]

            # Calculate an initial font size based on the bounding box dimensions
            font_size = h  # Start with the height of the bounding box
            font_size = min(font_size, max_font_size)  # Cap the font size at max_font_size
            font_size = max(font_size, min_font_size)  # Ensure font size doesn't go below min_font_size

            # Refine the font size to fit within the bounding box
            while font_size >= min_font_size:
                try:
                    font = ImageFont.truetype("arial.ttf", size=font_size)
                except IOError:
                    font = ImageFont.load_default()

                # Measure the height of a single line of text
                _, _, _, text_height = font.getbbox("A")  # Use a single character to measure line height

                # Wrap the text into multiple lines if necessary
                words = sentence.split(' ')
                lines = []
                current_line = ''

                for word in words:
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

                # Check if the wrapped text fits within the bounding box
                total_height = len(lines) * text_height
                if total_height <= h:
                    break  # Font size is acceptable

                # Reduce the font size if the text doesn't fit
                font_size -= 1

            # Draw the wrapped text
            for j, line in enumerate(lines):
                draw.text((x, y + j * text_height), line, fill="black", font=font)


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
    
input_pdf_path = 'sample.pdf'
output_pdf_path = 'translated_document.pdf'
process_pdf(input_pdf_path, output_pdf_path, dest_language='es')  # Translate to Spanish