# put stuff here
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

import tarfile, requests, PyIRI
from datetime import datetime, timedelta, timezone
from madrigalWeb.madrigalWeb import MadrigalData

# PyIRI
import PyIRI
import PyIRI.sh_library as sh

'''
activate virtual env

Download Pckg
python -m pip install madrigalWeb PyIRI pandas numpy matplotlib

To run program:
python research.py
'''

def run_pyiri_point(lat=37.2296, lon=-80.4139):
    now = datetime.now(timezone.utc)
    year, month, day = now.year, now.month, now.day

    aUT = np.array([12.0])
    # km
    aalt = np.arange(90, 1000, 5)
    F107 = 100

    hmF2_model = "SHU2015"
    foF2_coeff = "URSI"
    coord = "GEO"

    F2, F1, E, sun, mag, EDP = sh.IRI_density_1day(
        year, month, day, aUT,
        lon, lat, aalt, F107,
        coeff_dir=None,
        foF2_coeff=foF2_coeff,
        hmF2_model=hmF2_model,
        coord=coord
    )

    edp = np.array(EDP).squeeze()
    alt_m = aalt * 1000.0
    vtec_tecu = float(np.trapezoid(edp, alt_m) / 1e16)

    return {
        "date": f"{year:04d}-{month:02d}-{day:02d}",
        "lat": lat,
        "lon": lon,
        "alt_km": aalt,
        "edp_m3": edp,
        "vtec_tecu": vtec_tecu
    }

# Madrigal
def load_madrigal_experiments(days=30):
    end = datetime.now(timezone.utc)
    start = end - timedelta(days=days)

    md = MadrigalData("http://cedar.openmadrigal.org")
    exps = md.getExperiments(
        0,
        start.year, start.month, start.day, 0, 0, 0,
        end.year, end.month, end.day, 23, 59, 59,
        1
    )
    return exps

def plot_pyiri_profile(pyiri_out):
    plt.figure()
    plt.plot(pyiri_out["edp_m3"], pyiri_out["alt_km"])
    plt.xlabel("Electron density (m^-3)")
    plt.ylabel("Altitude (km)")
    plt.title(
        f"PyIRI Electron Density Profile\n"
        f"VTEC≈{pyiri_out['vtec_tecu']:.2f} TECU at ({pyiri_out['lat']:.2f},{pyiri_out['lon']:.2f})"
    )
    plt.tight_layout()
    plt.savefig("pyiri_edp_profile.png", dpi=200)

def plot_madrigal_daily_counts(exps):
    # pull date fields from objects or dicts
    rows = []
    for e in exps:
        def get_field(obj, name):
            if hasattr(obj, name):
                return getattr(obj, name)
            if isinstance(obj, dict):
                return obj.get(name)
            return None

        y = get_field(e, "startyear")
        m = get_field(e, "startmonth")
        d = get_field(e, "startday")
        if y and m and d:
            rows.append({"date": f"{int(y):04d}-{int(m):02d}-{int(d):02d}"})

    if not rows:
        print("Madrigal: could not extract start dates; skipping daily count plot.")
        return

    df = pd.DataFrame(rows)
    counts = df["date"].value_counts().sort_index()

    plt.figure()
    counts.plot(kind="bar")
    plt.xlabel("Date")
    plt.ylabel("Experiment count")
    plt.title("Madrigal Experiments per Day (last 30 days)")
    plt.tight_layout()
    plt.savefig("madrigal_experiments_per_day.png", dpi=200)

def main():
    #PyIRI run + visualize
    pyiri_out = run_pyiri_point()
    print("PyIRI: date =", pyiri_out["date"], "| VTEC (TECU) ≈", pyiri_out["vtec_tecu"])
    plot_pyiri_profile(pyiri_out)

    #Madrigal import + visualize
    exps = load_madrigal_experiments(days=30)
    print("Madrigal: experiments last 30 days =", len(exps))
    if exps:
        print("Madrigal sample:", exps[0])
    plot_madrigal_daily_counts(exps)

    print("Saved plots: pyiri_edp_profile.png, madrigal_experiments_per_day.png")

if __name__ == "__main__":
    main()