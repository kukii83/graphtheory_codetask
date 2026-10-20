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
3. Sample Cases & Outputs

   Case 1: ITS Campus Vicinity (Standard Test Case)
   - **Inputs:**
     - SPPG Latitude: `-7.28250`
     - SPPG Longitude: `112.79530`
     - Delivery Radius ($x$): `2.0 km`
     - Assumed Vehicle Speed: `30 km/h`
   - **Outputs:**
     - Total Distance: `23.84 km`
     - Estimated Time: `47.7 mins`
     - Schools Visited: `29`
     - Solver Runtime: `29.76 ms`
     - School Visiting Order (First 5 stops):
       1. SPPG Depot
       2. Sekolah Berkebutuhan Khusus Aditama (#23)
       3. SD Negeri Kalisari II (#21)
       4. TK, SD, SLTP Al - Azhar Kelapa Gading Surabaya (#19)
       5. Sekolah YPPI - 3 Surabaya (#6)

   Case 2: Surabaya City Center (Genteng / Tunjungan Area)
   - **Inputs:**
     - SPPG Latitude: `-7.26000`
     - SPPG Longitude: `112.74000`
     - Delivery Radius ($x$): `1.0 km`
     - Assumed Vehicle Speed: `30 km/h`
   - **Outputs:**
     - Total Distance: `~9.50 km`
     - Estimated Time: `~19.0 mins`
     - Schools Visited: `10 - 15 schools`
     - Solver Runtime: `< 15.00 ms`
     - Behavior: Dense urban routing accounting for one-way road constraints around downtown Surabaya.

   Case 3: Outskirts / Low-Density Boundary (Edge Case)
   - **Inputs:**
     - SPPG Latitude: `-7.32000`
     - SPPG Longitude: `112.82000`
     - Delivery Radius ($x$): `0.5 km`
     - Assumed Vehicle Speed: `30 km/h`
   - **Outputs:**
     - Schools Visited: `0` (or `1`)
     - Status: Displays a warning banner `No schools found within this radius. Increase the radius.`


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
