# A Practical Guide to LLM Deployment and RAG Systems / Materials

This repository contains all the material that was shown during the aforementioned training event.

You can find the material of Dr. Bakas from NCC Greece [here](https://colab.research.google.com/drive/1UK5GjSN7uj34N61PTzkwjXee7cfCyjO1?usp=sharing) on Google Colab.

## Running these notebooks

To run these notebooks you need a device with cuda GPUs. You can either use Google Colab, a local PC or if you have access to a hosting service.

### Create the Virtual Environment using UV

To install the required libraries, simply go into the directory that contains the *uv.lock* and *pyproject.toml* files and type:

```bash
uv sync
```

If you do not have UV installed, follow [these](https://docs.astral.sh/uv/getting-started/installation/) instructions.

UV will go ahead and create a *.venv* folder inside the directory.

Once you have the Virtual Env ready, you can go ahead and start running the jupyter notebooks.

## Running VLLM

Before running the launch scripts, you need to install the virtual environment as well. The procedure is the same with the one you did for the notebooks.

1. Install UV if not installed
2. Run *uv sync* inside the vllm directory where the *uv.lock* and *pyproject.toml* files are located.


To run the VLLM scripts you need to modify them a bit.

Specifically:
  - If you are not running on an HPC Facility, you need to remove the *SBATCH* part of the script.
  - You need to change these directories
    1. Source command: Point it to the directory of your *.venv*.

    ```bash
    source ${HOME}/vllm_launcher/.venv/bin/activate
    ```
    
    2. OUTPUT_FILE directory:

    ```bash
    OUTPUT_FILE=/nvme/scratch/${USER}$/llm.env
    ```

    3. HF_HOME directory. This is the directory where the HF models will be installed.

    ```bash
    export HF_HOME=/nvme/scratch/${USER}$/HF_cache 
    mkdir -p ${HF_HOME}
    ```
- Feel free to change the *vllm serve* parameters as well. You can find the documentation [here](https://docs.vllm.ai/en/latest/cli/serve.html?h=serve#vllm-serve)

---

#### Contact

For any questions feel free to reach out at mar.constantinou@cyi.ac.cy
