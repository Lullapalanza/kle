import mph

GDS_PATHS = [
    "C:/Users/nbr720/Documents/PhD/design/gds_files/D002_test0.gds",
    "C:/Users/nbr720/Documents/PhD/design/gds_files/D002_test1.gds",
]
MPH_PATH = "C:/Users/nbr720/Documents/PhD/design/comsol_mphs/eigenfrequency.mph"

client = mph.start()
model = client.load(MPH_PATH)

for gds_path in GDS_PATHS:
    geo_node = model/"geometries/Geometry 1/Import 1"
    geo_node.java.set("filename", gds_path)
    geo_node.java.importData()
    model.build()
    model.mesh()

    model.solve()
    print(
        gds_path,
        model.evaluate("emw.freq", "GHz"),
        model.evaluate("emw.Qfactor", "")
    )

model.clear()
model.reset()
model.save()