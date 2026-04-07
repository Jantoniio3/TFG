import os
from neo4j import GraphDatabase
from dotenv import load_dotenv

load_dotenv()

class Neo4jClient:
    def __init__(self):
        uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        user = os.getenv("NEO4J_USER", "neo4j")
        password = os.getenv("NEO4J_PASSWORD", "password")
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def execute_query(self, query, parameters=None):
        with self.driver.session() as session:
            result = session.run(query, parameters)
            return [record for record in result]
            
    def execute_write(self, query, parameters=None):
        with self.driver.session() as session:
            # For writing data specifically
            result = session.run(query, parameters)
            # return summary or data
            return result.consume()

    def get_all_concepts(self):
        query = "MATCH (c:Concepto) RETURN c.nombre as nombre ORDER BY c.nombre"
        resultados = self.execute_query(query)
        return [r["nombre"] for r in resultados]

    def get_prerequisites(self, concept_names):
        # Navega el grafo recursivamente hacia atrás a lo largo de las relaciones para encontrar todos los pre-requisitos funcionales
        query = """
        MATCH (pre:Concepto)-[*1..]->(c:Concepto)
        WHERE c.nombre IN $names
        RETURN DISTINCT pre.nombre as nombre
        """
        resultados = self.execute_query(query, {"names": concept_names})
        return [r["nombre"] for r in resultados]

    def clear_database(self):
        query = "MATCH (n) DETACH DELETE n"
        self.execute_query(query)

if __name__ == '__main__':
    # Test connection
    client = Neo4jClient()
    try:
        client.execute_query("RETURN 1")
        print("Conexión exitosa a Neo4j")
    except Exception as e:
        print(f"Error conectando a Neo4j: {e}")
    finally:
        client.close()
