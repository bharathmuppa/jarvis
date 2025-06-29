import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from llm_providers.openai_provider import OpenAIProvider
from neo4j import GraphDatabase
from neo4j.exceptions import CypherSyntaxError
from py2neo import Graph

node_properties_query = """
CALL apoc.meta.data()
YIELD label, other, elementType, type, property
WHERE NOT type = "RELATIONSHIP" AND elementType = "node"
WITH label AS nodeLabels, collect(property) AS properties
RETURN {labels: nodeLabels, properties: properties} AS output

"""

rel_properties_query = """
CALL apoc.meta.data()
YIELD label, other, elementType, type, property
WHERE NOT type = "RELATIONSHIP" AND elementType = "relationship"
WITH label AS nodeLabels, collect(property) AS properties
RETURN {type: nodeLabels, properties: properties} AS output
"""

rel_query = """
CALL apoc.meta.data()
YIELD label, other, elementType, type, property
WHERE type = "RELATIONSHIP" AND elementType = "node"
RETURN {source: label, relationship: property, target: other} AS output
"""

def schema_text(node_props, rel_props, rels):
    return f"""
        This is the schema representation of the Neo4j database.
        Node properties are the following:
        {node_props}
         Relationship properties are the following:
         {rel_props}
         Relationship point from source to target nodes
         {rels}
         Make sure to respect relationship types and directions
     """

class Neo4jGPTQuery:
    
    def __init__(self, url, user, password):
        self.url = url
        self.user = user
        self.password = password
        self.driver = GraphDatabase.driver(url, auth=(user, password))
        # construct schema
        self.schema = self.generate_schema()
    
    def generate_schema(self):
        node_props = self.query_database(node_properties_query)
        rel_props = self.query_database(rel_properties_query)
        rels = self.query_database(rel_query)
        return schema_text(node_props, rel_props, rels)
    
    def get_schema(self):
        # Connect to the Neo4j instance
        graph = Graph(self.url, auth=(self.user, self.password))
        # Get all labels in the graph
        labels_query = """
        MATCH (n)
        RETURN DISTINCT labels(n) AS labels
        """

        labels = graph.run(labels_query).to_table()
        labels = [label[0][0] for label in labels]

        # Get all relationships in the graph
        relationships_query = """
        CALL db.relationshipTypes() YIELD relationshipType
        RETURN relationshipType
        """

        relationships = graph.run(relationships_query).to_table()
        relationships = [relationship[0] for relationship in relationships]

        # Get the properties for each label
        node_properties = {}
        for label in labels:
            properties_query = f"""
            MATCH (n:{label})
            UNWIND keys(n) AS property
            RETURN DISTINCT property
            """
            properties = graph.run(properties_query).to_table()
            properties = [property[0] for property in properties]
            node_properties[label] = properties

        # Return the schema as a dictionary
        schema = {"labels": labels, "relationships": relationships, "node_properties": node_properties}
        return schema

    def get_system_message(self):
        return f"""
        Task: Generate Cypher queries to query a Neo4j graph database based on the provided schema definition.
        Instructions:
        Use only the provided relationship types and properties.
        Do not use any other relationship types or properties that are not provided.
        If you cannot generate a Cypher statement based on the provided schema, explain the reason to the user.
        Schema:
        {self.schema}

        Note: Do not include any explanations or apologies in your responses.
        """
    def query_database(self, neo4j_query, params={}):
        with self.driver.session() as session:
            result = session.run(neo4j_query, params)
            output = [r.values() for r in result]
            output.insert(0, result.keys())
            return output
    def refresh_schema(self):
        self.schema = self.generate_schema()

    def construct_cypher(self, question, history=None):
        # Initialize OpenAI provider
        openai_provider = OpenAIProvider()
        openai_provider.initialize()
        
        messages = [
            {"role": "system", "content": self.get_system_message()},
            {"role": "user", "content": question},
        ]
        # Used for Cypher healing flows
        if history:
            messages.extend(history)
            
        response = openai_provider.get_response(messages)
        return response.content if response.success else "Error generating Cypher query"      
    def run(self, question, history=None, retry=True):
        # Construct Cypher statement
        cypher = self.construct_cypher(question, history)
        print(cypher)
        
        try:
            return self.query_database(cypher)
        # If Cypher syntax error
        except CypherSyntaxError as e:
            # If out of retries
            if not retry:
                return "Invalid Cypher syntax"
            # Self-healing Cypher flow by
            # providing specific error to GPT-4
            print("Retrying")
            return self.run(
                question,
                [
                    {"role": "assistant", "content": cypher},
                    {
                        "role": "user",
                        "content": f"""This query returns an error: {str(e)} 
                        Give me a improved query that works without any explanations or apologies""",
                    },
                ],
                retry=False
            )