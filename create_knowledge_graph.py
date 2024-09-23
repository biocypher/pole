from biocypher import BioCypher
from pole.adapters.pole_adapter import (
    CustomAdapter,
)
from pole.adapters.aop_adapter import (
    CustomAOPAdapter,
)

bc = BioCypher(schema_config_path="config/schema_config_vhp.yaml")
#bc.show_ontology_structure(full=True)

adapter = CustomAdapter()
bc.write_nodes(adapter.get_nodes())
bc.write_edges(adapter.get_edges())

adapter = CustomAOPAdapter("data/AOP-Wiki-AOP.csv")
bc.write_nodes(adapter.get_nodes())
bc.write_edges(adapter.get_edges())

# Write admin import statement
bc.write_import_call()
bc.write_schema_info(as_node=True)

# Print summary
bc.summary()

# # Ontology information
# ont = bc._get_ontology()
# print(ont._nx_graph.nodes)
