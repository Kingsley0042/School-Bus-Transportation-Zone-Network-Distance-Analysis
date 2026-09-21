<img width="900" height="500" alt="Students by network distance to assigned school" src="https://github.com/user-attachments/assets/78a999d2-a0f2-4509-bf16-94f4b9e40296" />
<img width="900" height="500" alt="school_eligibility_comparison" src="https://github.com/user-attachments/assets/b21dedf8-b329-4687-af2e-85b0b2897fdf" />
<img width="3507" height="2480" alt="1-Mile Network Eligibility" src="https://github.com/user-attachments/assets/7cc5d631-a2ae-4559-a88d-0ea021f3e690" />
<img width="3507" height="2480" alt="0 5 Mile Network Eligibility" src="https://github.com/user-attachments/assets/c0f8bfeb-e01f-44a7-8d52-096393fa78f6" />
# School Bus Network Analysis

A GIS and network analysis project for evaluating school transportation eligibility using street-network distance.

## Project Overview

This project models student travel distances to assigned schools using a street network rather than straight-line distance. Student home locations were estimated from available address and street-range data, connected to the road network, and analyzed using shortest-path routing.

## Tools

* Python
* GeoPandas
* NetworkX
* QGIS
* Pandas

## Analysis

The analysis compares two transportation eligibility thresholds:

* **0.5 miles:** 7 students
* **1 mile:** 97 students

A total of **1,380 student locations** were successfully routed to their assigned schools.

The project includes school-level eligibility summaries, network-distance analysis, and QGIS maps comparing the two distance scenarios.

## Workflow

1. Process student address data.
2. Estimate student home locations from street address ranges.
3. Build a street-network graph.
4. Connect student homes and schools to the network.
5. Calculate shortest-path network distances.
6. Compare 0.5-mile and 1-mile eligibility.
7. Visualize results in QGIS.

## Limitations

Student home locations are approximate because they were derived from street address ranges rather than precise geocoding. The street network was modeled as bidirectional because the supplied street data did not provide a clear one-way field. Network distances therefore represent modeled results rather than official transportation routes.

## Outputs

* Network-distance distribution
* School eligibility comparison
* QGIS eligibility maps
* GeoPackage containing analysis results
