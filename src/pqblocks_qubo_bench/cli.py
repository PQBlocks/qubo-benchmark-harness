"""Command-line interface for the QUBO benchmarking system."""

import argparse
import logging
import os
import sys
import yaml
from typing import Dict, Any

from .pipeline import BenchmarkPipeline
from .batch import load_batch_config, execute_batch
# Removed test_data import


def load_config(config_path: str) -> Dict[str, Any]:
    """Load configuration from a YAML file."""
    with open(config_path, 'r') as f:
        return yaml.safe_load(f) or {}


def merge_config_with_env(config: Dict[str, Any]) -> Dict[str, Any]:
    """Merge configuration with environment variables."""
    # Override with environment variables
    if 'BENCH_HARNESS_SEED' in os.environ:
        config.setdefault('benchmark', {})['seed'] = int(os.environ['BENCH_HARNESS_SEED'])
    
    if 'OMP_NUM_THREADS' in os.environ:
        config.setdefault('benchmark', {})['threads_per_solver'] = int(os.environ['OMP_NUM_THREADS'])
    
    return config


def merge_config_with_cli_args(config: Dict[str, Any], args: argparse.Namespace) -> Dict[str, Any]:
    """Merge configuration with CLI arguments."""
    # Override with CLI arguments
    if args.min_runs is not None:
        config.setdefault('benchmark', {})['min_runs'] = args.min_runs
    
    if args.seed is not None:
        config.setdefault('benchmark', {})['seed'] = args.seed
    
    if args.threads is not None:
        config.setdefault('benchmark', {})['threads_per_solver'] = args.threads
    
    return config


def get_solver_by_id(solver_id: str):
    """Get a solver instance by its ID."""
    # This is a simplified implementation for demonstration
    # In a real implementation, this would map solver IDs to actual solver classes
    if solver_id == 'mock-solver':
        try:
            from .test_data.mock_instances import MOCK_BQM
            from .test_data.mock_solver import MockSolver
            return MockSolver(MOCK_BQM, seed=42)
        except ImportError:
            raise ValueError("mock-solver is not available in packaged release")
    else:
        raise ValueError(f"Unknown solver ID: {solver_id}")


def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(description='Bench-harness CLI for benchmarking quantum-inspired solvers.')
    
    # Subparsers for different commands
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # 'run' command
    run_parser = subparsers.add_parser('run', help='Run a benchmark on a specific instance')
    run_parser.add_argument('--solver', required=True, help='Solver identifier')
    run_parser.add_argument('--suite', required=True, help='Instance suite name')
    run_parser.add_argument('--instance', required=True, help='Instance identifier')
    run_parser.add_argument('--min-runs', type=int, help='Override minimum runs (≥100)')
    run_parser.add_argument('--seed', type=int, help='Override master seed')
    run_parser.add_argument('--threads', type=int, help='Override thread count')
    run_parser.add_argument('--output', help='Output path for benchmark card')
    
    # 'batch' command
    batch_parser = subparsers.add_parser('batch', help='Run a batch of benchmarks')
    batch_parser.add_argument('--config', required=True, help='Path to CSV configuration file')
    batch_parser.add_argument('--output-dir', default='results', help='Output directory for benchmark cards')
    
    # Parse arguments
    args = parser.parse_args()
    
    # If no command is specified, show help
    if args.command is None:
        parser.print_help()
        return
    
    # Handle 'run' command
    if args.command == 'run':
        # Load configuration
        config_path = os.environ.get('BENCH_HARNESS_CONFIG', 'config.yaml')
        if os.path.exists(config_path):
            config = load_config(config_path)
        else:
            config = {}
        
        # Merge with environment variables
        config = merge_config_with_env(config)
        
        # Merge with CLI arguments
        config = merge_config_with_cli_args(config, args)
        
        # Get solver
        try:
            solver = get_solver_by_id(args.solver)
        except ValueError as e:
            print(f"Error: {e}", file=sys.stderr)
            return 1
        
        # Create pipeline
        pipeline = BenchmarkPipeline(config)
        
        # Run benchmark
        try:
            card = pipeline.run(
                solver=solver,
                suite_name=args.suite,
                instance_id=args.instance,
                output_path=args.output
            )
            
            # Print summary
            print(f"Benchmark completed for {args.suite}/{args.instance}")
            print(f"Solver: {args.solver}")
            print(f"Success probability: {card['metrics']['success_probability']:.4f}")
            if card['metrics']['time_to_solution_99_seconds'] is not None:
                print(f"TTS(0.99): {card['metrics']['time_to_solution_99_seconds']:.6f} seconds")
            else:
                print("TTS(0.99): N/A (no successful runs)")
                
        except Exception as e:
            print(f"Error running benchmark: {e}", file=sys.stderr)
            return 1
        
        return 0
    
    # Handle 'batch' command
    elif args.command == 'batch':
        # Load configuration
        config_path = os.environ.get('BENCH_HARNESS_CONFIG', 'config.yaml')
        if os.path.exists(config_path):
            config = load_config(config_path)
        else:
            config = {}
        
        # Merge with environment variables
        config = merge_config_with_env(config)
        
        # Create pipeline
        pipeline = BenchmarkPipeline(config)
        
        # Load batch configuration
        try:
            batch_config = load_batch_config(args.config)
        except Exception as e:
            print(f"Error loading batch configuration: {e}", file=sys.stderr)
            return 1
        
        # Execute batch
        try:
            summary = execute_batch(batch_config, pipeline, args.output_dir)
            
            # Print summary
            print(f"Batch execution completed.")
            print(f"Total benchmarks: {summary['total_benchmarks']}")
            print(f"Successful: {summary['successful_benchmarks']}")
            print(f"Failed: {summary['failed_benchmarks']}")
            print(f"Success rate: {summary['success_rate']:.2%}")
                
        except Exception as e:
            print(f"Error executing batch: {e}", file=sys.stderr)
            return 1
        
        return 0
    
    # Handle unknown commands
    else:
        print(f"Unknown command: {args.command}", file=sys.stderr)
        parser.print_help()
        return 1


if __name__ == '__main__':
    sys.exit(main())