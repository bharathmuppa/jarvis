from flask import Flask,jsonify,request
from Agents import Neo4jGPTQuery


gds_db = Neo4jGPTQuery(
    url="bolt://44.199.213.212:7687",
    user="neo4j",
    password="coders-modification-dose"
    )

app = Flask(__name__)

@app.get("/neo4j/get_schema")
def getSchema():
    return gds_db.get_schema()

@app.post("/neo4j/gen_query")
def getQuery():
    request_data = request.get_json()
    return gds_db.run(request_data["query"])

if __name__=='__main__':
    app.run(debug=True)