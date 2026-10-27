"""Mock instances strictly for unit testing the harness pipeline."""

import dimod

MOCK_BQM = dimod.BinaryQuadraticModel({0: -1.0, 1: 1.0}, {(0, 1): -2.0}, 0.0, dimod.SPIN)
MOCK_INSTANCE_METADATA = {"suite_name": "MockSuite", "instance_id": "mock_2var", "num_variables": 2}
MOCK_REFERENCE_ENERGY = -1.0
