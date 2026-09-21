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
