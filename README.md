## Installation Guide

### 1. Clone the InterVox repository
```bash
git clone https://github.com/austinkangmusic/InterVox.git
```

### 2. Navigate to the InterVox directory
```bash
cd InterVox
```

### 3. Set up a virtual environment and activate it
```bash
& "D:\Private Server\Apps\PYTHON VERSIONS\python310\python.exe" -m venv venv
venv/Scripts/Activate
```

### 4. Find the path of the Python executable
```bash
Resolve-Path .\venv\Scripts\python.exe
```

### 5. Install the required dependencies
```bash
pip install -r requirements.txt
```

---

## Download an XTTS-v2 Model

First, create a directory and navigate to it:
```bash
mkdir XTTS-v2_models
cd XTTS-v2_models
```

Now, choose one of the models below to download:

**Yuki-Chan**
```bash
git clone https://huggingface.co/Xerror/XTTS-v2_Yuki-Chan
```

**C3PO**
```bash
git clone https://huggingface.co/Xerror/XTTS-v2_C3PO
```

**Pain**
```bash
git clone https://huggingface.co/Xerror/XTTS-v2_pain
```

**PeterJarvis**
```bash
git clone https://huggingface.co/Xerror/XTTS-v2_PeterJarvis
```

**S_Dogg**
```bash
git clone https://huggingface.co/Xerror/XTTS-v2_S_Dogg
```

**SamuelL**
```bash
git clone https://huggingface.co/Xerror/XTTS-v2_SamuelL
```

---

### 6. Run the main script
```bash
python main.py
```
