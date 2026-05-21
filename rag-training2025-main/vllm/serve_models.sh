#!/bin/bash

sbatch llm_launcher.sh &
sbatch embedder_launcher.sh &
sbatch ranker_launcher.sh &