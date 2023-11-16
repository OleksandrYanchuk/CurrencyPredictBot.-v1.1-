# CurrencyPredictBot v.1.1
## Telegram bot with ML model that predicts the approximate closing price at the end of the day of currency pairs.

## Setup and Local Installation

### To set up and run the project locally, follow these steps:

#### 1.  Clone the repository:

```python
https://github.com/OleksandrYanchuk/CurrencyPredictBot.-v1.1-.git
```
#### 2. Open the folder:
```python
cd CurrencyPredictBot.-v1.1-
```
#### 3. Create a virtual environment:
```python
python -m venv venv
```
#### 4. Activate the virtual environment:
   
##### - For Windows:
```python
venv\Scripts\activate
```
##### -	For macOS and Linux:
```python
source venv/bin/activate
```
#### 5. Setting up Environment Variables:

##### 1. Rename a file name `.env_sample` to `.env` in the project root directory.

##### 2. Make sure to replace all enviroment keys with your actual enviroment data.

#### 6. For run application manually make next steps:

```python
pip install -r requirements.txt
```
```python
python auto_task_start_day.py
```
```python
python predict_bot.py
```
#### 7. In the auto_task_hour.py file, set the time for the script to run
```python
python auto_task_hour.py
```
#### 8. In the auto_task_end_day.py file, set the time for the script to run
```python
python auto_task_end_day.py
```
