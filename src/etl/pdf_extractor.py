from markitdown import MarkItDown
import os

def extract_pdf_to_md(pdf_path, output_md_path):
    md = MarkItDown()
    print(f"Extrayendo texto de {pdf_path}...")
    result = md.convert(pdf_path)
    
    with open(output_md_path, 'w', encoding='utf-8') as f:
        f.write(result.text_content)
    
    print(f"Extracción completada. Guardado en {output_md_path}")
    return result.text_content

if __name__ == "__main__":
    pdf_path = os.path.join(os.path.dirname(__file__), '..', '..', 'recursos', 'Cuaderno de trabajo 2.pdf')
    out_path = os.path.join(os.path.dirname(__file__), '..', '..', 'recursos', 'cuaderno2_raw.md')
    if os.path.exists(pdf_path):
        extract_pdf_to_md(pdf_path, out_path)
    else:
        print(f"Error: No se encuentra el archivo en {pdf_path}")
