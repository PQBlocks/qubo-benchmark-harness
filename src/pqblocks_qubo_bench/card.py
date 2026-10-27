"""
Benchmark Card Generation module.
"""

from typing import Dict, Any, List
import jsonschema


# Define the JSON schema for benchmark cards
BENCHMARK_CARD_SCHEMA = {
    "type": "object",
    "properties": {
        "card_version": {"type": "string", "const": "1.0.0"},
        "metadata": {
            "type": "object",
            "properties": {
                "solver_id": {"type": "string"},
                "solver_name": {"type": "string"},
                "hardware": {
                    "type": "object",
                    "properties": {
                        "cpu": {"type": "string"},
                        "gpu": {"type": ["string", "null"]},
                        "threads_allocated": {"type": "integer"}
                    },
                    "required": ["cpu", "gpu", "threads_allocated"],
                    "additionalProperties": False
                },
                "parameters": {"type": "object"}
            },
            "required": ["solver_id", "solver_name", "hardware"],
            "additionalProperties": True
        },
        "benchmark_suite": {
            "type": "object",
            "properties": {
                "suite_name": {"type": "string"},
                "instance_id": {"type": "string"},
                "num_variables": {"type": "integer"},
                "num_edges": {"type": ["integer", "null"]}
            },
            "required": ["suite_name", "instance_id", "num_variables", "num_edges"],
            "additionalProperties": False
        },
        "execution_stats": {
            "type": "object",
            "properties": {
                "num_independent_runs": {"type": "integer", "minimum": 5},
                "average_single_run_time_seconds": {"type": "number"},
                "total_elapsed_time_seconds": {"type": "number"}
            },
            "required": ["num_independent_runs", "average_single_run_time_seconds", "total_elapsed_time_seconds"],
            "additionalProperties": False
        },
        "metrics": {
            "type": "object",
            "properties": {
                "target_energy": {"type": ["number", "null"]},
                "success_probability": {"type": "number", "minimum": 0, "maximum": 1},
                "time_to_solution_99_seconds": {"type": ["number", "null"]},
                "tts_95_confidence_interval": {
                    "type": "array",
                    "items": {"type": ["number", "null"]},
                    "minItems": 2,
                    "maxItems": 2
                },
                "best_energy_found": {"type": "number"},
                "reference_gap": {"type": ["number", "null"]}
            },
            "required": [
                "target_energy",
                "success_probability",
                "time_to_solution_99_seconds",
                "tts_95_confidence_interval",
                "best_energy_found",
                "reference_gap"
            ],
            "additionalProperties": False
        }
    },
    "required": ["card_version", "metadata", "benchmark_suite", "execution_stats", "metrics"],
    "additionalProperties": False
}


def generate_benchmark_card(
    solver_metadata: Dict[str, Any],
    instance_metadata: Dict[str, Any],
    execution_stats: Dict[str, Any],
    metrics: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Generate a benchmark card dictionary conforming to the schema.
    
    Args:
        solver_metadata: Solver information (solver_id, solver_name, hardware)
        instance_metadata: Instance information (suite_name, instance_id, num_variables, num_edges)
        execution_stats: Execution statistics (num_independent_runs, average_single_run_time_seconds, total_elapsed_time_seconds)
        metrics: Performance metrics (target_energy, success_probability, time_to_solution_99_seconds, 
                 tts_95_confidence_interval, best_energy_found, reference_gap)
                 
    Returns:
        Dictionary representing a benchmark card
    """
    # Handle special case: when success_probability is 0, time_to_solution_99_seconds should be null
    if metrics.get("success_probability") == 0.0:
        metrics = metrics.copy()  # Don't modify the original dict
        metrics["time_to_solution_99_seconds"] = None
        metrics["tts_95_confidence_interval"] = [None, None]
    
    card = {
        "card_version": "1.0.0",
        "metadata": solver_metadata,
        "benchmark_suite": instance_metadata,
        "execution_stats": execution_stats,
        "metrics": metrics
    }
    
    return card


def validate_benchmark_card(card: Dict[str, Any]) -> None:
    """
    Validate a benchmark card against the schema.
    
    Args:
        card: The benchmark card dictionary to validate
        
    Raises:
        jsonschema.exceptions.ValidationError: If the card doesn't conform to the schema
        jsonschema.exceptions.SchemaError: If the schema itself is invalid
    """
    validator = jsonschema.Draft7Validator(BENCHMARK_CARD_SCHEMA)
    validator.validate(card)