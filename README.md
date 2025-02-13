# CVAF

CVAF is a computer-vision based automation framework. It allows you to programatically spawn/control/kill a desktop environment. Additonally, it has a vision system that handles open-vocabulary pixel coordinate prediction for UI elements.

## Installation
Prerequisite: Install Docker

1. **Clone the repository:**

   ```bash
   git clone https://github.com/sampagon/CVAF.git
   cd CVAF
   ```

2. **Install dependencies:**  
    Only tested on Python 3.11 so far
    ```bash
    pip install -r requirements.txt
    ```

## Running Test
   This may take longer than expected on the first run because the desktop environment image and vision system need to be downloaded from dockerhub and huggingface, respectively.
   ```bash
   python test.py
   ```
## Demo

   https://github.com/user-attachments/assets/6096d26e-0ac1-4695-973b-735c62763372

