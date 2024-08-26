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
    CASE_STUDY = ":CaseStudy"
    ORGAN = ":Organ"



class CustomAdapterCaseStudyField(Enum):
    """
    Define possible fields the adapter can provide for case studies.
    """
    NAME = "case_study"

class CustomAdapterOrganField(Enum):
    """
    Define possible fields the adapter can provide for organs.
    """
    NAME = "organ"


class CustomAdapterEdgeType(Enum):
    """
    Define possible edges the adapter can provide.
    """
    STUDIES_AFFECT = "STUDIES_AFFECT"



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

        for case_study in self._data["case_study"].unique():
            yield (
                case_study,
                CustomAdapterNodeType.CASE_STUDY.value,
                {"name": case_study}
            )

        for organ in self._data["organ"].unique():
            yield (
                organ,
                CustomAdapterNodeType.ORGAN.value,
                {"name": organ}
            )

    def get_edges(self):
        """
        Returns a generator of edge tuples for edge types specified in the
        adapter constructor.
        """
        logger.info("Generating edges.")

        for index, row in self._data.iterrows():
            yield (
                None,
                row["case_study"],
                row["organ"],
                CustomAdapterEdgeType.STUDIES_AFFECT.value,
                {}
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

