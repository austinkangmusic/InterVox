## Installation
Get the folders.
1.
```bash
git clone https://github.com/austinkangmusic/InterVox.git
```

## cd to InterVox directory.
2.
```bash
cd InterVox
```

## Create a virtual environment, activate it and find the path of the python exe to select the intepreter.
3.
```bash
& "D:\Private Server\Apps\PYTHON VERSIONS\python310\python.exe" -m venv venv
venv/Scripts/Activate
Resolve-Path .\venv\Scripts\python.exe
```

## Install the requirements.
4.
```bash
pip install -r requirements.txt
```


## Choose a XTTS-v2 model to download.
5.
Here you go, without the numbers:

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

## Run.
6.
```bash
python main.py
```

