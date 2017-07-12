import matplotlib.pyplot as plt
import cartopy.feature as cfeature
import cartopy.crs as ccrs
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

data = pd.read_csv("bird_tracking.csv")
names = pd.unique(data.bird_name)    
eric = (data.bird_name=="Eric")

# PART 1 - TRAJECTORY

plt.figure(figsize=(7,7))
for bird in names:
    ind = (data.bird_name==bird)
    x, y = data.longitude[ind], data.latitude[ind]
    plt.plot(x, y, ".", label=bird)

plt.xlabel("Longitude")
plt.ylabel("Latitude")
plt.legend(loc="lower right")
plt.savefig("trajectories.pdf")

# PART 2 - ERIC'S SPEED

plt.figure(figsize=(8,4))
speed = data.speed_2d[eric]
ind = np.isnan(speed)

plt.hist(speed[~ind], bins=np.linspace(0, 30, 20), normed=True)
plt.xlabel("2D speed (m/s)")
plt.ylabel("Frequency")
plt.savefig("eric-speed.pdf")

# PART 3 - ERIC'S TIMEPLOT 

timestamps = []
for i in range(len(data)):
    time = data.date_time.iloc[i][:-3]
    time = datetime.strptime(time, "%Y-%m-%d %H:%M:%S")
    timestamps.append(time)
    
data["timestamp"] = pd.Series(timestamps, index=data.index)
times = data[eric].timestamp
elapsed_time = [time-times[0] for time in times]
elapsed_days = np.array(elapsed_time) / timedelta(days=1)

plt.plot(elapsed_days)
plt.xlabel("Observations")
plt.ylabel("Elapsed time (days)")
plt.savefig("eric-timeplot.pdf")

# PART 4 - ERIC'S MIGRATION PATTERN

inds = []
speeds = []
next_day = 1
for i, t in enumerate(elapsed_days):
    if t < next_day:
        inds.append(i)

    else:
        # Compute mean speed and clean
        mean = np.mean(data.speed_2d[inds])
        speeds.append(mean)
        next_day += 1; inds = []

plt.figure(figsize=(8,6))
plt.plot(speeds)
plt.xlabel("Day")
plt.ylabel("Mean speed (m/s)")
plt.savefig("eric-pattern.pdf")

# PART 5 - THE MAP

plt.figure(figsize=(10,10))
ax = plt.axes(projection=ccrs.Mercator())
ax.set_extent((-25.0, 20.0, 52.0, 10.0))
ax.add_feature(cfeature.LAND)
ax.add_feature(cfeature.OCEAN)
ax.add_feature(cfeature.COASTLINE)
ax.add_feature(cfeature.BORDERS, linestyle=":")

for name in names:
    ind = (data["bird_name"] == name)
    x, y = data.longitude[ind], data.latitude[ind]
    ax.plot(x, y, ".", transform=ccrs.Geodetic(), label=name)

plt.legend(loc="upper left")
plt.savefig("map.pdf")

# PART 6 - ALL BIRDS' MIGRATION PATTERN

datetimes = pd.to_datetime(data.date_time)
data["date"] = datetimes.dt.date
birds = data.groupby("bird_name")

plt.figure()
for name in names:
    bird = birds.get_group(name).groupby("date")
    speed = bird.speed_2d.mean()
    speed.plot(label=name)

plt.legend(loc="upper left")
plt.savefig("patterns.pdf")
