import re
import os
import json

def parse_markdown_to_exercises(md_filepath):
    with open(md_filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    parts = re.split(r'(?i)Ejercicios\s+(resueltos|propuestos)', content)
    
    exercises = []
    exercise_pattern = re.compile(r'\n(\d+\.\s*(?:\(\*\)\s*)?)')
    
    if len(parts) >= 3:
        resueltos_content = parts[2]
        resueltos_splits = exercise_pattern.split(resueltos_content)
        for i in range(1, len(resueltos_splits), 2):
            numero_str = resueltos_splits[i].strip()
            texto = resueltos_splits[i+1].strip()
            # Limpiar posible basura del pie de pagina como cuado incluye "Programación I"
            texto = re.sub(r'Programación I – Cuaderno.*?(\n|$)', '', texto, flags=re.DOTALL)
            texto = texto.strip()
            if texto:
                exercises.append({
                    "id": f"resuelto_{numero_str.replace('.', '').replace('(*)', '').strip()}",
                    "estado": "Resuelto",
                    "enunciado": texto
                })
            
    if len(parts) >= 5:
        propuestos_content = parts[4]
        propuestos_splits = exercise_pattern.split(propuestos_content)
        for i in range(1, len(propuestos_splits), 2):
            numero_str = propuestos_splits[i].strip()
            texto = propuestos_splits[i+1].strip()
            texto = re.sub(r'Programación I – Cuaderno.*?(\n|$)', '', texto, flags=re.DOTALL)
            texto = texto.strip()
            if texto:
                exercises.append({
                    "id": f"propuesto_{numero_str.replace('.', '').replace('(*)', '').strip()}",
                    "estado": "Propuesto",
                    "enunciado": texto
                })

    return exercises

if __name__ == "__main__":
    md_path = os.path.join(os.path.dirname(__file__), '..', '..', 'cuaderno2_raw.md')
    ejercicios = parse_markdown_to_exercises(md_path)
    print(f"Búsqueda finalizada. Ejercicios encontrados: {len(ejercicios)}")
    
    out_path = os.path.join(os.path.dirname(__file__), '..', '..', 'ejercicios_parseados.json')
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(ejercicios, f, ensure_ascii=False, indent=2)
    print(f"Guardados como JSON en: {out_path}")
