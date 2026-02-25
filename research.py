# put stuff here
import tarfile, requests
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
    return requests.get("https://services.swpc.noaa.gov/text/us-tec-total-electron-content.txt", timeout=60).text

def madrigal(days=30):
    end = datetime.now(timezone.utc); start = end - timedelta(days=days)
    md = MadrigalData("http://cedar.openmadrigal.org")
    exps = md.getExperiments(0, start.year, start.month, start.day, 0,0,0, end.year, end.month, end.day, 23,59,59, 1)
    return len(exps)

print("IRI files:", iri())
print("NOAA chars:", len(noaa()))
print("Madrigal count:", madrigal())