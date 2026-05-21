#!/bin/bash -l

#SBATCH --job-name=llm_serve
#SBATCH --partition=gpu # Partition
#SBATCH --nodes=1 # Number of nodes
#SBATCH --gres=gpu:2 #Number of GPUs
#SBATCH --ntasks-per-node=1  # Number of tasks
#SBATCH --cpus-per-task=20
#SBATCH --output=logs/llm_launcher.%j.out # Stdout (%j=jobId)
#SBATCH --error=logs/llm_launcher.%j.err # Stderr (%j=jobId)
#SBATCH --time=4:00:00 # Walltime
#SBATCH -A p308 # Accounting project

# Make sure your have been granted access to the model
export MODEL_NAME="meta-llama/Llama-3.1-8B-Instruct" # "google/gemma-3-27b-it" "meta-llama/Llama-3.1-8B-Instruct" "openai/gpt-oss-20b"

# Load any necessary modules
source ${HOME}/vllm_launcher/.venv/bin/activate

# Define the file path you want to clean up
OUTPUT_FILE=/nvme/scratch/${USER}/llm.env
echo $OUTPUT_FILE

# Function to clean up the file
function cleanup {
    echo "Job terminating, cleaning up files..."
    if [ -f $OUTPUT_FILE ]; then
        rm -f $OUTPUT_FILE
        echo "Removed file: $OUTPUT_FILE"
    else
        echo "File not found: $OUTPUT_FILE"
    fi
    exit
}

# Set up trap to catch signals
# This ensures cleanup happens when job is terminated for any reason
trap cleanup EXIT SIGTERM SIGINT 

HOSTNAME=$(hostname)

# Generate random ports for Jupyter and Ollama
PORT=$(shuf -i 10000-60000 -n 1)


# Choose a directory for the cache 
export HF_HOME=/nvme/scratch/${USER}/HF_cache
mkdir -p ${HF_HOME}

#Set it to the number of GPU per node
export TENSOR_PARALLEL_SIZE=${SLURM_GPUS_ON_NODE}

#debuging
export VLLM_LOGGING_LEVEL=DEBUG

export OMP_NUM_THREADS=${SLURM_CPUS_PER_TASK}

API_KEY="token-abc123"

# Prepare the message to be displayed and saved to a file
CONNECTION_MESSAGE=$(cat <<EOF
VLLM_LLM_PORT=${PORT}
VLLM_LLM_HOST=${HOSTNAME}
VLLM_LLM_URL=http://${HOSTNAME}:${PORT}
VLLM_API_KEY=${API_KEY}
MODEL_NAME=${MODEL_NAME}
EOF
)

# Print the connection details to both the terminal and a txt file
echo "$CONNECTION_MESSAGE" | tee $OUTPUT_FILE

echo "Starting server"
srun vllm serve ${MODEL_NAME} \
    --task generate \
    --tensor-parallel-size ${TENSOR_PARALLEL_SIZE} \
    --no-enable-chunked-prefill \
    --disable-custom-all-reduce \
    --enforce-eager \
    --dtype float16 \
    --max-model-len 2048 \
    --api-key ${API_KEY} \
    --host ${HOSTNAME} \
    --port ${PORT}