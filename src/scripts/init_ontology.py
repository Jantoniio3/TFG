import os
import sys

# Add src to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from src.database.neo4j_client import Neo4jClient

def parse_txt_and_populate(filepath):
    print("Iniciando conexión a Neo4j y parseo del archivo...")
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    parts = content.split("RELACIONES ENTRE CONCEPTOS")
    concepts_part = parts[0]
    relations_part = parts[1] if len(parts) > 1 else ""

    client = Neo4jClient()
    # Limpiamos la BD para evitar duplicados si corremos esto múltiples veces
    client.clear_database()

    # 1. Parse Concepts
    current_topic = ""
    concept_nodes = []
    
    for line in concepts_part.split('\n'):
        line = line.strip()
        if not line or line.startswith('-') or line.startswith('*'):
            continue
            
        if line.startswith('Tema'):
            current_topic = line
        else:
            concept_name = line
            concept_nodes.append({"name": concept_name, "topic": current_topic})

    # Insert Concepts
    print(f"Insertando {len(concept_nodes)} conceptos de la teoría...")
    for concept in concept_nodes:
        query = """
        MERGE (c:Concepto {nombre: $name})
        SET c.tema = $topic
        """
        client.execute_write(query, {"name": concept["name"], "topic": concept["topic"]})

    # 2. Parse Relations
    print("Procesando relaciones entre conceptos...")
    relation_lines = relations_part.split('\n')
    for line in relation_lines:
        line = line.strip()
        if not line or line.startswith('*'):
            continue
            
        if '@' not in line:
            continue
            
        parts = line.split('@', 1)
        source_part = parts[0].strip()
        rest_part = parts[1].strip()
        
        # Clean source part (soporta "[Concepto]" y "Concepto]")
        source_concept = source_part.replace('[', '').replace(']', '').strip()
        
        if ' ' not in rest_part:
            continue
            
        relation_type, targets_part = rest_part.split(' ', 1)
        relation_type = relation_type.strip().upper() # PREREQUISITO_DE, DEPENDE_DE
        
        # Clean targets part
        targets = [t.replace('[', '').replace(']', '').strip() for t in targets_part.split(',')]
        
        for target_concept in targets:
            # Query para linkear, asegurándonos de que ambos nodos existan
            query = f"""
            MATCH (a:Concepto {{nombre: $source}})
            MATCH (b:Concepto {{nombre: $target}})
            MERGE (a)-[r:{relation_type}]->(b)
            """
            client.execute_write(query, {"source": source_concept, "target": target_concept})

    client.close()
    print("¡Ontología inicializada exitosamente en Neo4j!")

if __name__ == '__main__':
    # Ruta asumiendo ejecución desde src/scripts/
    filepath = os.path.join(os.path.dirname(__file__), '..', '..', 'Lista conceptos Programación por tema.txt')
    parse_txt_and_populate(filepath)
