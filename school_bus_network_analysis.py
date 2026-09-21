import geopandas as gpd
import pandas as pd
import networkx as nx
from shapely.geometry import Point

# -----------------------------

# 1. Load street network

# -----------------------------

streets = gpd.read_file(
r"streets\tgr_str_cl.shp"
)

print("Street CRS:", streets.crs)
print("Street segments:", len(streets))

# -----------------------------

# 2. Load student data

# -----------------------------

students = pd.read_excel(
r"Student List with bus stop and home to school distances.xlsx"
)

print("Students:", len(students))

# -----------------------------

# 3. Define school locations

# -----------------------------

schools = gpd.GeoDataFrame(
{
"School": ["KWO", "KVA", "KWA", "KIA", "KTA", "KHS"],
"geometry": [
Point(-90.2555, 38.5746),
Point(-90.2366, 38.6625),
Point(-90.2359, 38.6415),
Point(-90.2108, 38.6456),
Point(-90.2392, 38.6642),
Point(-90.2461, 38.6388),
],
},
crs="EPSG:4326",
)

schools = schools.to_crs(streets.crs)

# -----------------------------

# 4. Build street network

# -----------------------------

G = nx.Graph()

for _, row in streets.iterrows():
coords = list(row.geometry.coords)

```
for a, b in zip(coords[:-1], coords[1:]):
    distance = Point(a).distance(Point(b))

    G.add_edge(
        a,
        b,
        length=distance
    )
```

print("Network nodes:", G.number_of_nodes())
print("Network edges:", G.number_of_edges())
print("Connected components:", nx.number_connected_components(G))

# -----------------------------

# 5. Connect schools to network

# -----------------------------

school_nodes = {}

for _, school in schools.iterrows():

```
school_point = school.geometry

nearest_index = streets.geometry.distance(
    school_point
).idxmin()

street_geometry = streets.loc[
    nearest_index, "geometry"
]

connection_point = street_geometry.interpolate(
    street_geometry.project(school_point)
)

nearest_endpoint = min(
    list(street_geometry.coords),
    key=lambda x: Point(x).distance(connection_point)
)

connection_distance = Point(
    nearest_endpoint
).distance(connection_point)

school_node = tuple(
    connection_point.coords[0]
)

G.add_node(
    school_node,
    school=school["School"]
)

G.add_edge(
    school_node,
    nearest_endpoint,
    length=connection_distance
)

school_nodes[school["School"]] = school_node
```

# -----------------------------

# 6. Prepare student addresses

# -----------------------------

student_addr = students.copy()

student_addr["HouseNum"] = pd.to_numeric(
student_addr["Home House #"],
errors="coerce"
)

student_addr["Zip5"] = pd.to_numeric(
student_addr["Home Zip Code"].astype(str).str[:5],
errors="coerce"
)

student_addr["StreetClean"] = (
student_addr["Home Street"]
.astype(str)
.str.upper()
.str.replace("NORTH", "N", regex=False)
.str.replace("SOUTH", "S", regex=False)
.str.replace("EAST", "E", regex=False)
.str.replace("WEST", "W", regex=False)
.str.replace("STREET", "ST", regex=False)
.str.replace("AVENUE", "AVE", regex=False)
.str.replace("DRIVE", "DR", regex=False)
.str.replace("ROAD", "RD", regex=False)
)

student_addr["StreetName"] = (
student_addr["StreetClean"]
.str.replace(
r"^(N|S|E|W)\s+",
"",
regex=True
)
.str.replace(
r"\s+(ST|AVE|DR|RD|BLVD|PL|CT|LN|WAY|PKWY)$",
"",
regex=True
)
.str.strip()
)

streets["StreetNameClean"] = (
streets["STREETNAME"]
.astype(str)
.str.upper()
.str.strip()
)

# -----------------------------

# 7. Match addresses to streets

# -----------------------------

street_matches = []

for idx, row in student_addr.iterrows():

```
matches = streets[
    streets["StreetNameClean"]
    == row["StreetName"]
]

if pd.isna(row["HouseNum"]) or matches.empty:
    street_matches.append(None)
    continue

valid = matches[
    (
        (
            row["HouseNum"]
            >= matches["FROMLEFT"]
        )
        &
        (
            row["HouseNum"]
            <= matches["TOLEFT"]
        )
    )
    |
    (
        (
            row["HouseNum"]
            >= matches["FROMRIGHT"]
        )
        &
        (
            row["HouseNum"]
            <= matches["TORIGHT"]
        )
    )
]

if valid.empty:
    street_matches.append(None)
else:
    street_matches.append(valid.index[0])
```

student_addr["StreetSegment"] = street_matches

# -----------------------------

# 8. Estimate home locations

# -----------------------------

def calculate_fraction(row):

```
if pd.isna(row["StreetSegment"]):
    return None

street = streets.loc[
    row["StreetSegment"],
    "geometry"
]

house_number = row["HouseNum"]

left_min = streets.loc[
    row["StreetSegment"],
    "FROMLEFT"
]

left_max = streets.loc[
    row["StreetSegment"],
    "TOLEFT"
]

right_min = streets.loc[
    row["StreetSegment"],
    "FROMRIGHT"
]

right_max = streets.loc[
    row["StreetSegment"],
    "TORIGHT"
]

candidates = []

if left_min <= house_number <= left_max:
    candidates.append(
        (
            house_number - left_min
        )
        /
        (
            left_max - left_min
        )
        if left_max != left_min
        else 0
    )

if right_min <= house_number <= right_max:
    candidates.append(
        (
            house_number - right_min
        )
        /
        (
            right_max - right_min
        )
        if right_max != right_min
        else 0
    )

if not candidates:
    return None

return sum(candidates) / len(candidates)
```

student_addr["Fraction"] = student_addr.apply(
calculate_fraction,
axis=1
)

student_addr["HomePoint"] = student_addr.apply(
lambda row:
streets.loc[
row["StreetSegment"],
"geometry"
].interpolate(
row["Fraction"],
normalized=True
)
if pd.notna(row["Fraction"])
and 0 <= row["Fraction"] <= 1
else None,
axis=1
)

# -----------------------------

# 9. Connect homes to network

# -----------------------------

network_nodes = gpd.GeoDataFrame(
{
"node": list(G.nodes)
},
geometry=[
Point(node)
for node in G.nodes
],
crs=streets.crs
)

home_gdf = gpd.GeoDataFrame(
student_addr[
student_addr["HomePoint"].notna()
].copy(),
geometry="HomePoint",
crs=streets.crs
)

home_gdf = gpd.sjoin_nearest(
home_gdf,
network_nodes[["node", "geometry"]],
how="left",
distance_col="NodeDistance"
)

home_gdf = home_gdf[
~home_gdf.index.duplicated(
keep="first"
)
]

# -----------------------------

# 10. Calculate school distances

# -----------------------------

all_distances = {}

for school in school_nodes:

```
all_distances[school] = (
    nx.single_source_dijkstra_path_length(
        G,
        school_nodes[school],
        weight="length"
    )
)
```

home_gdf["NetworkDistanceFt"] = [
all_distances[
row["School Abbrev"]
].get(row["node"])
for _, row in home_gdf.iterrows()
]

home_gdf["NetworkDistanceMiles"] = (
home_gdf["NetworkDistanceFt"] / 5280
)

# -----------------------------

# 11. Calculate eligibility

# -----------------------------

home_gdf["Eligible_0_5mi"] = (
home_gdf["NetworkDistanceMiles"] <= 0.5
)

home_gdf["Eligible_1_0mi"] = (
home_gdf["NetworkDistanceMiles"] <= 1.0
)

# -----------------------------

# 12. School-level summary

# -----------------------------

summary = home_gdf.groupby(
"School Abbrev"
).agg(
Students=(
"NetworkDistanceMiles",
"count"
),
Eligible_0_5mi=(
"Eligible_0_5mi",
"sum"
),
Eligible_1_0mi=(
"Eligible_1_0mi",
"sum"
)
)

summary["Pct_0_5mi"] = (
summary["Eligible_0_5mi"]
/
summary["Students"]
* 100
)

summary["Pct_1_0mi"] = (
summary["Eligible_1_0mi"]
/
summary["Students"]
* 100
)

print("\nSchool Eligibility Summary:")
print(summary.round(2))

# -----------------------------

# 13. Export results

# -----------------------------

home_gdf.to_file(
"student_home_network_results.gpkg",
layer="students",
driver="GPKG"
)

schools.to_file(
"student_home_network_results.gpkg",
layer="schools",
driver="GPKG"
)

print("\nAnalysis complete.")
print("Results exported to student_home_network_results.gpkg")
