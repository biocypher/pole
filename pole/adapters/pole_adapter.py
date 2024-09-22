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
    CASESTUDY = ":CaseStudy"
    ORGAN = ":Organ"
    CHEMICAL = ":Chemical"
    MODEL_SYSTEM = ":Model_system"
    COMPUTATIONAL_MODEL = ":Computational_model"
    BIOASSAY = ":Bioassay"
    EXPERIMENTAL_CONDITION = ":Experimental_condition"
    MEASURABLE_ENDPOINT = ":Measurable_endpoint"


class CustomAdapterCaseStudyField(Enum):
    """
    Define possible fields the adapter can provide for case studies.
    """
    NAME = "CaseStudyName"
    DESCRIPTION = "CaseStudyDescription"

class CustomAdapterOrganField(Enum):
    """
    Define possible fields the adapter can provide for organs.
    """
    NAME = "OrganName"

class CustomAdapterChemicalField(Enum):
    """
    Define possible fields the adapter can provide for chemicals.
    """
    NAME = "ChemicalName"
    CAS = "ChemicalCAS"
    SMILES = "SMILES"                   # New property
    INCHIKEY = "InChIKey"               # New property
    CHEMICAL_GROUP = "chemical_group"   # New property

class CustomAdapterModelSystemField(Enum):
    """
    Define possible fields the adapter can provide for model systems.
    """
    NAME = "ModelSystemName"
    CELL_TYPE = "ModelSystemCellType"
    DESCRIPTION = "ModelSystemDescription"

class CustomAdapterComputationalModelField(Enum):
    """
    Define possible fields the adapter can provide for computational models.
    """
    NAME = "ComputationalModelName"
    TYPE = "ComputationalModelType"
    LANGUAGE = "ComputationalModelLanguage"
    INPUT = "ComputationalModelInput"
    OUTPUT = "ComputationalModelOutput"

class CustomAdapterBioassayField(Enum):
    """
    Define possible fields the adapter can provide for bioassays.
    """
    NAME = "BioassayName"
    MEASURED = "Measured"

class CustomAdapterExperimentalConditionField(Enum):
    EXPOSURE_DURATION = "exposure_duration"
    EXPOSURE_CONCENTRATION = "exposure_concentration"
    CONDITION_NAME = "condition_name"
    DESCRIPTION = "ExperimentalConditionDescription"

class CustomAdapterMeasurableEndpointField(Enum):
    NAME = "MeasurableEndpointName"
    DESCRIPTION = "MeasurableEndpointDescription"
    TYPE = "MeasurableEndpointType"


class CustomAdapterEdgeType(Enum):
    """
    Define possible edges the adapter can provide.
    """
    case_study_related_organ = "case_study_related_organ"
    case_study_relevant_chemical = "case_study_relevant_chemical"
    case_study_relevant_model_system = "case_study_relevant_model_system"
    case_study_relevant_computational_model = "case_study_relevant_computational_model"
    chemical_measured_with_bioassay = "chemical_measured_with_bioassay"
    bioassay_executed_on_model_system = "bioassay_executed_on_model_system"
    bioassay_related_organ = "bioassay_related_organ"
    chemical_relevant_to_computational_model = "chemical_relevant_to_computational_model"
    chemical_measured_in_model_system = "chemical_measured_in_model_system"
    model_system_relevant_to_organ = "model_system_relevant_to_organ"
    computational_model_relevant_to_organ = "computational_model_relevant_to_organ"
    case_study_relevant_endpoint = "case_study_relevant_endpoint"
    bioassay_used_with_experimental_condition = "bioassay_used_with_experimental_condition"
class CustomAdapter:
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
        data = pd.read_csv("data/Combined_output.csv", dtype=str)

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
            if _type == ':CaseStudy':
                _props['name'] = row.get('CaseStudyName', None)
                _props['description'] = row.get('CaseStudyDescription', None)
            elif _type == ':Organ':
                _props['name'] = row.get('OrganName', None)
            elif _type == ':Chemical':
                _props['name'] = row.get('ChemicalName', None)
                _props['CAS'] = row.get('ChemicalCAS', None)
                _props['SMILES'] = row.get('SMILES', None)  
                _props['InChIKey'] = row.get('InChIKey', None)    
                _props['chemical_group'] = row.get('chemical_group', None)
            elif _type == ':Model_system':
                _props['name'] = row.get('ModelSystemName', None)
                _props['cell_type'] = row.get('ModelSystemCellType', None)
                _props['description'] = row.get('ModelSystemDescription', None)
            elif _type == ':Computational_model':
                _props['name'] = row.get('ComputationalModelName', None)
                _props['type'] = row.get('ComputationalModelType', None)
                _props['language'] = row.get('ComputationalModelLanguage', None)
                _props['input'] = row.get('ComputationalModelInput', None)
                _props['output'] = row.get('ComputationalModelOutput', None)
            elif _type == ':Bioassay':
                _props['name'] = row.get('BioassayName', None)
                _props['measured'] = row.get('Measured', None)
            elif _type == ':Experimental_condition':
                _props['exposure_duration'] = row.get('exposure_duration', None)
                _props['exposure_concentration']= row.get('exposure_concentration', None)
                _props['condition_name']= row.get('condition_name', None)
                _props['description']= row.get('ExperimentalConditionDescription', None)
            elif _type == ':Measurable_endpoint':
                _props['name'] = row.get('MeasurableEndpointName', None)  # Should match the CSV field name
                _props['description'] = row.get('MeasurableEndpointDescription', None)  # Should match the CSV field name
                _props['type'] = row.get('MeasurableEndpointType', None)  # Should match the CSV field name

        

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
                    CustomAdapterCaseStudyField,
                    CustomAdapterOrganField,
                    CustomAdapterChemicalField,
                    CustomAdapterModelSystemField,
                    CustomAdapterComputationalModelField,
                    CustomAdapterBioassayField,
                    CustomAdapterExperimentalConditionField,
                    CustomAdapterMeasurableEndpointField,
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
