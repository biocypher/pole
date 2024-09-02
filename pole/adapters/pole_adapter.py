import random
import string
import pandas as pd
from enum import Enum, auto
from itertools import chain
from typing import Optional
from biocypher._logger import logger

logger.debug(f"Loading module {__name__}.")


class CustomAdapterNodeType(Enum):
    """
    Define types of nodes the adapter can provide.
    """
    CASESTUDY = ":CaseStudy"
    ORGAN = ":organ"



class CustomAdapterCaseStudyField(Enum):
    """
    Define possible fields the adapter can provide for case studies.
    """
    NAME = "CaseStudy"

class CustomAdapterOrganField(Enum):
    """
    Define possible fields the adapter can provide for organs.
    """
    NAME = "organ"


class CustomAdapterEdgeType(Enum):
    """
    Define possible edges the adapter can provide.
    """
    case_study_related_organ = "case_study_related_organ"



class CustomAdapter:
    """
    Adapter for creating a knowledge graph from the case study and organ data.
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
        self._organ_data = self._get_organ_data()

        # print unique _labels
        print(f"Unique labels: {self._data['_labels'].unique()}")
        # print unique _type
        print(f"Unique types: {self._data['_type'].unique()}")

    def _get_node_data(self):
        """
        Get all rows that do not have a _type.
        """
        return self._data[self._data["_type"].isnull()]

    def _get_edge_data(self):
        """
        Get all rows that have a _type.
        """
        return self._data[self._data["_type"].notnull()]
    
    def _get_organ_data(self):
        """
        Subset to only case study organ relationships.
        """
        return self._data[self._data["_type"] == "case_study_related_organ"][["_start", "_end"]]
    
    def _get_organ(self, _id):
        """
        Get organ for case study.
        """
        if not _id in self._organ_data["_start"].values:
            return None

        organ_id = self._organ_data[self._organ_data["_start"] == _id]["_end"].values[0]
        organ = self._data[self._data["_id"] == organ_id]["organ"].values[0]
        #print(organ)
        #print(organ_id)
        return organ

    def _read_csv(self):
        """
        Read data from CSV file.
        """
        logger.info("Reading data from CSV file.")
        return pd.read_csv("data/case_study_organ.csv", dtype=str)

    def get_nodes(self):
        """
        Returns a generator of node tuples for node types specified in the
        adapter constructor.
        """
        logger.info("Generating nodes.")
        
        node_count = 0
        for index, row in self._node_data.iterrows():
            _id = row["_id"]
            _type = row["_labels"]  # Don't strip the colon if it's part of the label
            
            logger.info(f"Processing node: ID={_id}, Type={_type}")

            if _type not in self.node_types:
                logger.info(f"Skipping node with ID={_id} due to type mismatch.")
                continue

            _props = {}
            if _type == ':CaseStudy':
                _props['name'] = row.get('CaseStudy', None)
            elif _type == ':organ':
                _props['name'] = row.get('organ', None)
            
            logger.info(f"Yielding node: ID={_id}, Type={_type}, Properties={_props}")
            node_count += 1
            yield (
                _id,
                _type,
                _props,
            )
        
        logger.info(f"Total nodes generated: {node_count}")


    def get_edges(self):
        """
        Returns a generator of edge tuples for edge types specified in the
        adapter constructor.
        """
        logger.info("Generating edges.")

        for index, row in self._data.iterrows():
            if row["_type"] not in self.edge_types:
                continue

            _id = None
            _start = row["_start"]
            _end = row["_end"]
            _type = row["_type"]
            _props = {}
            yield (
                _id,
                _start,
                _end,
                _type,
                _props,
            )

    def _set_types_and_fields(self, node_types, node_fields, edge_types, edge_fields):
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
                    CustomAdapterCaseStudyField,
                    CustomAdapterOrganField,
                )
            ]

        if edge_types:
            self.edge_types = [type.value for type in edge_types]
        else:
            self.edge_types = [type.value for type in CustomAdapterEdgeType]

        if edge_fields:
            self.edge_fields = [field.value for field in edge_fields]
        else:
            self.edge_fields = []

