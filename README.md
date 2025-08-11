Requirements: 
Python version >=3.10, <3.12
CUDA-enabled GPU. The CUDA version supported by the NVIDIA driver needs to be >= 12.4.

Note:
update the .env file with your env variables.
check custom.yaml for the env variables
copy the custom.yaml inside OpenAvatarChat/config

after cloning, run:
sudo apt install git-lfs
git lfs install 
git submodule update --init --recursive

to download add openavatarchat dependent modules please run:
cd OpenAvatarChat
git submodule update --init --recursive
git clone --depth 1 https://huggingface.co/facebook/wav2vec2-base-960h ./models/wav2vec2-base-960h
wget https://huggingface.co/3DAIGC/LAM_audio2exp/resolve/main/LAM_audio2exp_streaming.tar -P ./models/LAM_audio2exp/
tar -xzvf ./models/LAM_audio2exp/LAM_audio2exp_streaming.tar -C ./models/LAM_audio2exp && rm ./models/LAM_audio2exp/LAM_audio2exp_streaming.tar

pip install uv
uv venv --python 3.11.11
uv pip install setuptools pip
uv run install.py --uv --config <absolute path to config file>.yaml
./scripts/post_config_install.sh --config <absolute path to config file>.yaml

to run the avatar:
uv run src/demo.py --config <absolute path to config file>.yaml




