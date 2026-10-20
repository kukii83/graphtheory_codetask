# ITS Graph Theory class Group 5 Coding Task (Week 6-8)

Group 5 Members:

-Maulana Anugra Putra/5025251159 (kukii83)

-I Gusti Agung Candra Nugraha/5025251169 (candranugraha576)

-Hussein Mohammad Mahsun/5025251170 (TheDelightOFice)

In this task we will be doing 3 coding tasks which is:
- Travelling Salesman Problem
- Chinese Postman Problem
- The Knight's Tour

### Prerequisites
- Python 3.x interpreter installed
- Standard Python built-in libraries

### How to Run
- **Travelling Salesman:**
1. Prerequisites:
   - Compiler (VSCode, or any that works with Python)
   - Python 3.10 or above
   - `pip` package manager
2. Steps:
   - download both `app.py` and `download_data.py` into one folder
   - open VSCode
   - download the dependencies needed with:
     ```bash
     pip install osmnx networkx geopandas folium streamlit streamlit-folium scikit-learn
     ```
   - run the `download_data.py` program:
     ```bash
     python download_data.py
     ```
   - Two files, `cache/surabaya_road.graphml` and `cache/schools_surabaya.geojson` should appear in your folder after that
   - Open the website with:
     ```bash
     python -m streamlit run app.py
     ```


- **Chinese Postman:**


- **The Knight's Tour:**
1. Clone this repo and open it in Visual Studio Code
2. Open terminal and run:
```
"python knightstour.py"
```
3. Input the sample cases (see below) and you will get the output results

### Sample Cases
- **Travelling Salesman:**


- **Chinese Postman:**


- **The Knight's Tour:**
1. Example from PPT slide:
   ```
   5 5
   2 2
   ```
   
2. Starting from a corner:
   ```
   8 8
   3 4
   ```

3. Starting from center:
   ```
   6 6
   3 2
   ```

4. Samples that will print "Path not found":
   ```
   3 3
   0 0
   ```
   ```
   4 4
   0 0
   ```
   ```
   5 5
   9 9
   ```
