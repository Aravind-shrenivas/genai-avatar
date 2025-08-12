## Requirements
- **Python**: `>=3.10, <3.12`
- **CUDA-enabled GPU**  
  - NVIDIA driver must support **CUDA ≥ 12.4**

---

## 1. Environment Configuration
1. Update the `.env` file with your environment variables.
2. Check `custom.yaml` for the required variables.
3. Copy `custom.yaml` into:
   ```bash
   OpenAvatarChat/config
   ```

---

## 2. Initial Setup
After cloning the repository:
```bash
sudo apt install git-lfs
git lfs install
sudo apt install ffmpeg
git submodule update --init --recursive
```

---

## 3. Download Dependent Modules
```bash
cd OpenAvatarChat

# Update submodules
git submodule update --init --recursive

# Clone wav2vec2 model
git clone --depth 1 https://huggingface.co/facebook/wav2vec2-base-960h ./models/wav2vec2-base-960h

# Download and extract LAM_audio2exp model
wget https://huggingface.co/3DAIGC/LAM_audio2exp/resolve/main/LAM_audio2exp_streaming.tar -P ./models/LAM_audio2exp/
tar -xzvf ./models/LAM_audio2exp/LAM_audio2exp_streaming.tar -C ./models/LAM_audio2exp
rm ./models/LAM_audio2exp/LAM_audio2exp_streaming.tar
```

---

## 4. Python Virtual Environment Setup
```bash
pip install uv
uv venv --python 3.11.11
uv pip install setuptools pip
```

---

## 5. Install Project Dependencies
```bash
uv run install.py --uv --config <absolute path to config file>.yaml
./scripts/post_config_install.sh --config <absolute path to config file>.yaml
```

---

## 6. Run the Avatar
```bash
uv run main.py --config <absolute path to config file>.yaml
```

---

## Notes
- Ensure your **CUDA version** is compatible with your GPU driver before proceeding.
- Always use the **absolute path** for the config file when running install or demo commands.
