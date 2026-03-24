# put stuff here
import tarfile, requests, PyIRI, io
import xarray as xr
import numpy as np
from datetime import datetime, timedelta, timezone
from madrigalWeb.madrigalWeb import MadrigalData
'''
activate virtual env

Download Pckg
python -m pip install requests madrigalWeb

To run program:
python research.py
'''
def iri():
    with tarfile.open("00_iri.tar") as t:
        return t.getnames()[:10]

def noaa():
    #Grabbing data from web
    text = requests.get("https://services.swpc.noaa.gov/text/us-tec-total-electron-content.txt", timeout=60).text ### WEBSITE CURRENTLY DOWN; ERROR IS THROWN
    lines = text.splitlines()

    ###Returning website 404 to prevent errors###
    return text

    #Finding the starting blocks of data
    block_starts = [i for i, line in enumerate(lines) if line.strip().startswith("0 -1500")]
    start = block_starts[0]

    #Separating into longitude headers and TEC values
    lon_line = lines[start]
    longitudes = np.array(list(map(int, lon_line.split()))[1:]) / 10 #Scaled down by 10 since the values in the dataset are multiplied by 10 in order to remove decimal and store in integers

    #Rest of the data not a longitude
    block_data = lines[start+1:]

    #idk chatgpt helepd cook this one up
    raw = np.loadtxt(io.StringIO("\n".join(block_data)))

    #Rest of data scaled and stored separating also latitude headers
    latitudes = raw[:, 0] / 10
    tec_values = raw[:, 1:] / 10

    #Formated into dataarray
    da = xr.DataArray(
        tec_values,
        coords={
            "latitude": latitudes,
            "longitude": longitudes
        },
        dims=["latitude", "longitude"],
        name="TEC"
    )
    return da

def madrigal(days=30):
    end = datetime.now(timezone.utc); start = end - timedelta(days=days)
    md = MadrigalData("http://cedar.openmadrigal.org")
    exps = md.getExperiments(0, start.year, start.month, start.day, 0,0,0, end.year, end.month, end.day, 23,59,59, 1)
    return len(exps)

print("IRI files:", iri())
print("NOAA: ", noaa())
print("Madrigal count:", madrigal())