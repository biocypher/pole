import pandas as pd
from enum import Enum
from itertools import chain
from typing import Optional
from biocypher._logger import logger

logger.debug(f"Loading module {__name__}.")

class CustomAdapterNodeType(Enum):
    """
    Define types of nodes the adapter can provide.
    """
    AOP = ":AOP"
    KEY_EVENT = ":KeyEvent"
    STRESSOR = ":Stressor"


class CustomAdapterAOPField(Enum):
    """
    Define possible fields the adapter can provide for AOP.
    """
    NAME = "AOPName"
    ID = "AOPID"
    CREATOR = "AOPcreator"
    DESCRIPTION = "AOPDescription"
    SOURCE = "AOPsource"

class CustomAdapterKEField(Enum):
    """
    Define possible fields the adapter can provide for Key Event (KE).
    """
    NAME = "KEName"  # Field from your CSV
    ID = "KEID"
    DESCRIPTION = "KEDescription"

class CustomAdapterEdgeType(Enum):
    """
    Define possible edges the adapter can provide.
    """
    AOP_INCLUDES_MIE = "AOP_includes_mie"
    AOP_INCLUDES_AO = "AOP_includes_ao"
    AOP_INCLUDES_KEY_EVENT = "AOP_includes_key_event"
    AOP_RELEVANT_STRESSOR = "AOP_relevant_stressor"


class CustomAOPAdapter:
    """
    Adapter for creating a knowledge graph
    """

    def __init__(self, aop_file: str, ke_file: str):
        """
        Initialize with two input files: AOP file and KE file.
        """
        self.aop_file = aop_file  # Store AOP file path
        self.ke_file = ke_file    # Store KE file path
        self._node_data, self._edge_data = self._read_and_format_aop_csv()  # Read AOP data
        self._ke_data = self._read_ke_csv()  # Read KE data

        # Check if '_labels' column exists, if not, assume a default label
        if '_labels' not in self._node_data.columns:
            logger.warning(f"'_labels' column not found, assigning default label ':AOP' for all nodes.")
            self._node_data['_labels'] = ':AOP'

        # Print unique _labels and _types for debugging
        print(f"Unique labels: {self._node_data['_labels'].unique()}")
        print(f"Unique types: {self._edge_data['_type'].unique()}")


    def _read_ke_csv(self):
        """
        Read Key Event (KE) data from the KE CSV file.
        """
        logger.info(f"Reading Key Event (KE) data from {self.ke_file}.")
        ke_data = pd.read_csv(self.ke_file, dtype=str)

        # Ensure the necessary columns exist in the KE data
        if 'KEID' not in ke_data.columns:
            raise ValueError("KE file must contain 'KEID' column.")
        
        # Return the KE data
        return ke_data


    def _read_and_format_aop_csv(self):
        """
        Read and format data from CSV file, adding edges and cleaning types.
        """
        logger.info(f"Reading and formatting data from {self.aop_file}.")

        data = pd.read_csv(self.aop_file, dtype=str)

        # Check if _type column exists, if not, handle nodes and edges separately
        if "_type" not in data.columns:
            logger.warning(f"'_type' column not found, assuming implicit handling of nodes and edges.")
            data["_type"] = None  # Create a placeholder for the type

        # Clean whitespace in _type column if it exists
        if "_type" in data.columns:
            data["_type"] = data["_type"].str.strip()

        # Create edges based on related columns (MIE, AO, AOPKE, and AOPStressor)
        # MIE edge
        mie_edges = data[["AOPID", "MIE"]].dropna().copy()
        mie_edges["_start"] = mie_edges["AOPID"]
        mie_edges["_end"] = mie_edges["MIE"]
        mie_edges["_type"] = "AOP_includes_mie"

        # AO edge
        ao_edges = data[["AOPID", "AO"]].dropna().copy()
        ao_edges["_start"] = ao_edges["AOPID"]
        ao_edges["_end"] = ao_edges["AO"]
        ao_edges["_type"] = "AOP_includes_ao"

        # AOPKE edge (Key Event)
        key_event_edges = data[["AOPID", "AOPKE"]].dropna().copy()
        key_event_edges["_start"] = key_event_edges["AOPID"]
        key_event_edges["_end"] = key_event_edges["AOPKE"]
        key_event_edges["_type"] = "AOP_includes_key_event"

        # AOPStressor edge
        stressor_edges = data[["AOPID", "AOPStressor"]].dropna().copy()
        stressor_edges["_start"] = stressor_edges["AOPID"]
        stressor_edges["_end"] = stressor_edges["AOPStressor"]
        stressor_edges["_type"] = "AOP_relevant_stressor"

        # Combine all edge data into one dataframe
        edges = pd.concat([mie_edges, ao_edges, key_event_edges, stressor_edges], ignore_index=True)

        # Return formatted data and edges as separate datasets
        return data, edges


    def get_nodes(self):
        """
        Returns a generator of node tuples for node types specified in the
        adapter constructor, including KE nodes.
        """
        logger.info("Generating nodes.")

        # First, yield the AOP nodes
        for index, row in self._node_data.iterrows():
            _id = row.get("AOPID", None)
            _type = row.get("_labels", ":AOP")
            _props = {
                'name': row.get('AOPName', None),
                'creator': row.get('AOPcreator', None),
                'description': row.get('AOPDescription', None),
                'source': row.get('AOPsource', None)
            }
            logger.info(f"Yielding AOP node: ID={_id}, Type={_type}, Properties={_props}")
            yield (_id, _type, _props)

        # Then, yield the KE nodes
        for index, row in self._ke_data.iterrows():
            _id = row.get("KEID", None)
            _type = ":KeyEvent"  # Default label for Key Event nodes
            _props = {
                'name': row.get('KEName', None),
                'description': row.get('KEDescription', None)
            }
            logger.info(f"Yielding KE node: ID={_id}, Type={_type}, Properties={_props}")
            yield (_id, _type, _props)


    def get_edges(self):
        """
        Returns a generator of edge tuples for edge types specified in the
        adapter constructor.
        """
        logger.info("Generating edges.")

        for index, row in self._edge_data.iterrows():
            _id = None  # Edge ID can be auto-generated or skipped
            _start = row["_start"]
            _end = row["_end"]
            _type = row["_type"]
            _props = {}

            #logger.info(f"Yielding edge: Start={_start}, End={_end}, Type={_type}, Properties={_props}")
            yield (_id, _start, _end, _type, _props)

