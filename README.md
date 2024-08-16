# POLE Crime Demo dataset - BioCypher & BioChatter

We use the [pole
dataset](https://github.com/neo4j-graph-examples/pole/tree/main) to demonstrate
the building of a BioCypher knowledge graph and the facilitation of querying the
graph using BioChatter and ChatGSE. The dataset is a public dataset from
Manchester, U.K.


## ⚙️ Installation (local using Docker)
To start a local instance of the Neo4j database and BioChatter Light, clone the
repository and run the Docker compose setup. [Docker](https://www.docker.com/)
needs to be installed and running on your machine.

> :warning: Important note: For using the OpenAI GPT model that is called from
BioChatter Light, you need to provide your OpenAI API key through the environment
variable `OPENAI_API_KEY`. If you do not provide a key, the query generation
will fail.

```{bash}
git clone https://github.com/biocypher/pole.git
cd pole
export OPENAI_API_KEY=sk-...  # or add it to your .bashrc or .zshrc
docker compose up -d
```

## 🛠 Usage

The Docker compose workflow will take care of building the database, importing
and deploying in Neo4j, and starting the BioChatter Light app. Given you have provided
your API key, you can now open the BioChatter Light app in your browser at
[http://localhost:8501](http://localhost:8501). To query the knowledge graph,
navigate to the `Knowledge Graph` tab, set the database IP to `deploy` (the name
of the Docker service that runs the Neo4j database). Now you should be able to 
see the query text interface. Entering a query and confirming with `Enter` will 
generate a query and execute it on the database. The generated query and results 
will be displayed in the space below the interface. You can modify the query and 
rerun it (`CMD+Enter` on Mac, `Ctrl+Enter` on Windows) without having to call 
the LLM again. To generate a new query, simply update the query text.

Some example queries:
- `where happened most crimes`
- `who committed the most crimes`
- `who knows people that committed many crimes while not being criminal themselves`

You can also visit [http://localhost:7474](http://localhost:7474) to access the
Neo4j browser interface. It requires no authentication (simply press `Connect`)
and allows you to explore the database and run Cypher queries.
