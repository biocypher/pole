import pandas as pd
from enum import Enum
from itertools import chain
from typing import Optional
from biocypher._logger import logger

logger.debug(f"Loading module {__name__}.")

class CompoundWikiAdapterNodeType(Enum):
    """
    Define types of nodes the adapter can provide.
    """
    CHEMICAL = ":Chemical"

class CompoundWikiAdapterChemicalField(Enum):
    """
    Define possible fields the adapter can provide for chemicals.
    """
    NAME = "ChemicalName"
    CAS = "ChemicalCAS"
    SMILES = "SMILES"                   # New property
    INCHIKEY = "InChIKey"               # New property

class CompoundWikiAdapter:
    """
    Adapter for creating a knowledge graph
    """

    def __init__(
        self,
        node_types: Optional[list] = None,
        node_fields: Optional[list] = None,
        edge_types: Optional[list] = None,
        edge_fields: Optional[list] = None,
    ):
        self._set_types_and_fields(node_types, node_fields, edge_types, edge_fields)
        self._data = self._read_csv()
        self._node_data = self._get_node_data()
        self._edge_data = self._get_edge_data()

        # Print unique _labels and _types for debugging
        print(f"Unique labels: {self._data['_labels'].unique()}")
        print(f"Unique types: {self._data['_type'].unique()}")

    def _read_csv(self):
        """
        Read data from CSV file and clean edge type column.
        """
        logger.info("Reading data from CSV file.")
        data = pd.read_csv("data/CompoundWiki_output.csv", dtype=str)

        # Clean whitespace from the _type column to avoid issues
        data["_type"] = data["_type"].str.strip()

        return data

    def _get_node_data(self):
        """
        Get all rows that do not have a _type (i.e., nodes).
        """
        return self._data[self._data["_type"].isnull()]

    def _get_edge_data(self):
        """
        Get all rows that have a _type (i.e., edges).
        """
        return self._data[self._data["_type"].notnull()]

    def get_nodes(self):
        """
        Returns a generator of node tuples for node types specified in the
        adapter constructor.
        """
        logger.info("Generating nodes.")

        node_count = 0
        for index, row in self._node_data.iterrows():
            _id = row["_id"]
            _type = row["_labels"]

            if _type not in self.node_types:
                logger.info(f"Skipping node with ID={_id} due to type mismatch.")
                continue

            _props = {}
            if _type == ':Chemical':
                _props['name'] = row.get('ChemicalName', None)
                _props['CAS'] = row.get('ChemicalCAS', None)
                _props['SMILES'] = row.get('SMILES', None)
                _props['InChIKey'] = row.get('InChIKey', None)

            logger.info(f"Yielding node: ID={_id}, Type={_type}, Properties={_props}")
            node_count += 1
            yield (_id, _type, _props)

        logger.info(f"Total nodes generated: {node_count}")

    def get_edges(self):
        """
        Returns a generator of edge tuples for edge types specified in the
        adapter constructor.
        """
        logger.info("Generating edges.")

        edge_count = 0
        for index, row in self._edge_data.iterrows():
            if row["_type"] not in self.edge_types:
                logger.warning(f"Edge type {row['_type']} not in specified edge types.")
                continue

            _id = None  # Edges don't necessarily need unique IDs
            _start = row["_start"]
            _end = row["_end"]
            _type = row["_type"]
            _props = {}
            logger.info(f"Yielding edge: Start={_start}, End={_end}, Type={_type}, Properties={_props}")
            edge_count += 1
            yield (_id, _start, _end, _type, _props)

        logger.info(f"Total edges generated: {edge_count}")

    def _set_types_and_fields(self, node_types, node_fields, edge_types, edge_fields):
        """
        Set the types and fields for nodes and edges, if specified. Otherwise, use defaults.
        """
        if node_types:
            self.node_types = [type.value for type in node_types]
        else:
            self.node_types = [type.value for type in CustomAdapterNodeType]

        if node_fields:
            self.node_fields = [field.value for field in node_fields]
        else:
            self.node_fields = [
                field.value
                for field in chain(
                    CompoundWikiAdapterChemicalField,
                )
            ]

        if edge_types:
            self.edge_types = [type.value for type in edge_types]
        else:
            self.edge_types = [type.value for type in CompoundWikiAdapterEdgeType]

        if edge_fields:
            self.edge_fields = [field.value for field in edge_fields]
        else:
            self.edge_fields = []
