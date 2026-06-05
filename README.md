# Tic Tac Toe Cloud Computing
Repository made for cloud computing

## 📂 Folder Structure

```
tictactoe/
├── .gitignore
├── app.py
├── requirements.txt
├── Dockerfile
```

## 🛠 Setup Instructions

Follow these steps to run the project locally.

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/Sannebeast/tictactoe.git
cd tictactoe
```

### 2️⃣ Install Python (if needed)

* Python 3.11+ is required.
* Download from: [https://www.python.org/downloads/windows/](https://www.python.org/downloads/windows/)
* Make sure to check **"Add Python to PATH"** during installation.
* Verify installation:

```bash
python --version
```

### 3️⃣ Create a Virtual Environment

```bash
python -m venv venv
```

This will create a local virtual environment in the `venv/` folder.

### 4️⃣ Activate the Virtual Environment

#### Command Prompt (cmd)

```bash
venv\Scripts\activate
```

#### PowerShell

```powershell
.\venv\Scripts\Activate.ps1
```

You should see the prompt change to:

```
(venv) C:\path\to\tictactoe>
```

### 5️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

