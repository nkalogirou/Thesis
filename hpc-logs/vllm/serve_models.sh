#!/bin/bash
# Submit all three vLLM services (LLM, embedder, reranker) as separate Slurm jobs.

sbatch llm_launcher.sh &
sbatch embedder_launcher.sh &
sbatch ranker_launcher.sh &