import pandas as pd

pd.set_option("display.max_columns", None)

from biocypher import BioCypher
from pole.adapters.pole_adapter import (
    PoleAdapter,
    # PoleAdapterNodeType,
    # PoleAdapterEdgeType,
    # PoleAdapterProteinField,
    # PoleAdapterDiseaseField,
)

bc = BioCypher()
ont = bc._get_ontology()
print(ont._nx_graph.nodes)

adapter = PoleAdapter()
# nodes = list(adapter.get_nodes())
bc.write_nodes(adapter.get_nodes())
bc.write_edges(adapter.get_edges())

# Write admin import statement
bc.write_import_call()

# Print summary
bc.summary()
