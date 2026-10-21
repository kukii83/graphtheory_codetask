# ITS Graph Theory class Group 5 Coding Task (Week 6-8)

Group 5 Members:

- Maulana Anugra Putra/5025251159 (kukii83)

- I Gusti Agung Candra Nugraha/5025251169 (candranugraha576)

- Hussein Mohammad Mahsun/5025251170 (TheDelightOFice)

In this task we will be doing 3 coding tasks which is:
- Travelling Salesman Problem
- Chinese Postman Problem
- The Knight's Tour

### Prerequisites
- Python 3.x interpreter installed
- Standard Python built-in libraries

## How to Run
### Travelling Salesman
1. Steps:
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
   - Two files, `cache/surabaya_road.graphml` and `cache/schools_surabaya.geojson` should appear in your folder after that, inside a folder named `cache`
   - Open the website with:
     ```bash
     python -m streamlit run app.py
     ```
     Just in case:
   - If `download_data.py` doesn't work, download the `cache.zip` file
   - Extract the zip file, once you open it, you should see `cache/surabaya_road.graphml` and `cache/schools_surabaya.geoson` inside
   - Keep those two inside the folder, put this `cache` folder inside the main project folder
   - Open the website with:
     ```bash
     python -m streamlit run app.py
     ```

2. Sample Cases & Outputs

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
      - Solver Runtime: `27.41 ms`
      - School Visiting Order (First 5 stops):
         1. SPPG Depot
         2. Sekolah Berkebutuhan Khusus Aditama (#23)
         3. SD Negeri Kalisari II (#21)
         4. TK, SD, SLTP Al - Azhar Kelapa Gading Surabaya (#19)
         5. Sekolah YPPI - 3 Surabaya (#6)
         <img width="2560" height="1440" alt="image" src="https://github.com/user-attachments/assets/72f50e86-4c79-49d3-8fe4-8bac4367472e" />


   Case 2: Surabaya City Center (Genteng / Tunjungan Area)
   - **Inputs:**
     - SPPG Latitude: `-7.26000`
     - SPPG Longitude: `112.74000`
     - Delivery Radius ($x$): `1.0 km`
     - Assumed Vehicle Speed: `30 km/h`
   - **Outputs:**
     - Total Distance: `~22.45 km`
     - Estimated Time: `~44.9 mins`
     - Schools Visited: `27 schools`
     - Solver Runtime: `< 6.40 ms`
     - School Visiting Order (First 5 stops):
      1. SMK Kesehatan Nusantara (#6)
      2. SMA Trimurti (#7)
      3. SD Negeri Kaliasin 1 & 3 (#5)
      4. Yayasan Kemala Bhayangkari (#3)
      5. SMP Kristen Petra 2 Surabaya (#27)
     <img width="2560" height="1440" alt="image" src="https://github.com/user-attachments/assets/080d8ccd-7cfb-4dfe-8e63-687ff2d1bd1c" />


   Case 3: Outskirts / Low-Density Boundary (Edge Case)
   - **Inputs:**
     - SPPG Latitude: `-7.32000`
     - SPPG Longitude: `112.82000`
     - Delivery Radius ($x$): `0.5 km`
     - Assumed Vehicle Speed: `30 km/h`
   - **Outputs:**
     - Schools Visited: `0` (or `1`)
     - Status: Displays a warning banner `No schools found within this radius. Increase the radius.`
     <img width="2560" height="1440" alt="image" src="https://github.com/user-attachments/assets/be835b7d-3640-4b4c-8876-90fdc68f620b" />


## Chinese Postman

1. Steps:
   - download all the file of Chinese Postman into one folder
   - open VSCode
   - download the dependencies needed with:
     ```bash
     py -m pip install -r requirements.txt
     ```
   - Open the website with:
     ```bash
     py -m streamlit run app.py
     ```

2. Sample Cases & Outputs

   Case 1: Offline demo grid (tick “Offline demo grid”)
   - **Inputs:**
     - SPPG Latitude: `-7.2575`
     - SPPG Longitude: `112.7521`
     - Delivery Radius ($x$): `1.5 km`
     - Assumed Vehicle Speed: `60 km/h`
   - **Outputs:**
     <img width="1321" height="768" alt="image" src="https://github.com/user-attachments/assets/58549426-a770-4e25-912d-98e3b1550b63" />
     <img width="1326" height="829" alt="image" src="https://github.com/user-attachments/assets/f1bb73d3-bf74-4faa-92f4-f8e1b44de30c" />


   Case 2: Downtown, near Tugu Pahlawan
   - **Inputs:**
     - SPPG Latitude: `-7.2459`
     - SPPG Longitude: `112.7378`
     - Delivery Radius ($x$): `1.0 km`
     - Assumed Vehicle Speed: `60 km/h`
   - **Outputs:**
     <img width="1314" height="757" alt="image" src="https://github.com/user-attachments/assets/a193010f-21a9-4f29-aef6-597630a7dfc0" />
     <img width="1351" height="829" alt="image" src="https://github.com/user-attachments/assets/5c826bd9-9ea1-4eac-835b-d318ddac2423" />



   Case 3: Surabaya Zoo (Kebun Binatang) area
   - **Inputs:**
     - SPPG Latitude: `-7.2954`
     - SPPG Longitude: `112.7367`
     - Delivery Radius ($x$): `3 km`
     - Assumed Vehicle Speed: `60 km/h`
   - **Outputs:**
    <img width="1312" height="761" alt="image" src="https://github.com/user-attachments/assets/627709d5-f4f2-4118-9b98-686baa162c3f" />
    <img width="1336" height="829" alt="image" src="https://github.com/user-attachments/assets/1acd76e7-5fdc-44c6-b10c-5dbd14041d3c" />


## The Knight's Tour
1. Clone this repo and open it in Visual Studio Code
2. Open terminal and run:
```
"python knightstour.py"
```
3. Input the sample cases (see below) and you will get the output results\

Sample Cases:
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


AI use:
https://share.gemini.google/buzi1Nz823R4
