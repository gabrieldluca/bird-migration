import matplotlib.pyplot as plt
import cartopy.feature as cfeature
import cartopy.crs as ccrs
import pandas as pd
import numpy as np
import datetime

birddata = pd.read_csv("bird_tracking.csv")
bird_names = pd.unique(birddata.bird_name)    

# PART 1 - TRAJECTORY
plt.figure(figsize=(7,7))
for bird in bird_names:
    ix = birddata.bird_name==bird
    (x, y) = (birddata.longitude[ix], birddata.latitude[ix])
    plt.plot(x,y,'.', label=bird)

plt.xlabel("Longitude")
plt.ylabel("Latitude")
plt.legend(loc="lower right")
plt.savefig("trajectories.pdf")

# PART 2 - ERIC'S SPEED
ix = birddata.bird_name=='Eric'
speed = birddata.speed_2d[ix]
ind = np.isnan(speed)
plt.hist(speed[~ind])

plt.figure(figsize=(8,4))
speed = birddata.speed_2d[birddata.bird_name=='Eric']
ind = np.isnan(speed)
plt.hist(speed[~ind], bins=np.linspace(0, 30, 20), normed=True)
plt.xlabel("2D speed (m/s)")
plt.ylabel("Frequency")
plt.savefig("eric_speed.pdf")

# PART 3 - ERIC'S TIMEPLOT 
timestamps = []
for k in range(len(birddata)):
    timestamps.append(datetime.datetime.strptime(birddata.date_time.iloc[k][:-3], "%Y-%m-%d %H:%M:%S"))
    
birddata["timestamp"] = pd.Series(timestamps, index=birddata.index)

data = birddata[birddata.bird_name=='Eric']
times = data.timestamp
elapsed_time = [time-times[0] for time in times]
elapsed_days = np.array(elapsed_time) / datetime.timedelta(days=1)

plt.plot(elapsed_days)
plt.xlabel("Observations")
plt.ylabel("Elapsed time (days)")
plt.savefig("eric_timeplot.pdf")

# PART 4 - ERIC'S MIGRATION PATTERN
next_day = 1
inds = []
speeds = []
for (i, t) in enumerate(elapsed_days):
    if t < next_day:
        inds.append(i)
    else: #compute mean speed
        speeds.append(np.mean(data.speed_2d[inds]))
        next_day += 1
        inds = []

plt.figure(figsize=(8,6))
plt.plot(speeds)
plt.xlabel("Day")
plt.ylabel("Mean speed (m/s)")
plt.savefig("eric_pattern.pdf")

# PART 5 - THE MAP
proj = ccrs.Mercator()

plt.figure(figsize=(10,10))
ax = plt.axes(projection=proj)
ax.set_extent((-25.0, 20.0, 52.0, 10.0))
ax.add_feature(cfeature.LAND)
ax.add_feature(cfeature.OCEAN)
ax.add_feature(cfeature.COASTLINE)
ax.add_feature(cfeature.BORDERS, linestyle=':')

for name in bird_names:
    ix = birddata['bird_name'] == name
    (x,y) = (birddata.longitude[ix], birddata.latitude[ix])
    ax.plot(x, y, '.', transform=ccrs.Geodetic(), label=name)

plt.legend(loc="upper left")
plt.savefig("map.pdf")

# PART 6 - ALL BIRDS' MIGRATION PATTERN
birddata.date_time = pd.to_datetime(birddata.date_time)
birddata["date"] = birddata.date_time.dt.date

grouped_birds = birddata.groupby("bird_name")
grouped_bydates = birddata.groupby("date")
grouped_birdday = birddata.groupby(["bird_name", "date"])

mean_speeds = grouped_birds.speed_2d.mean()
mean_altitudes = grouped_birds.altitude.mean()
mean_altitudes_perday = grouped_bydates.altitude.mean()
mean_altitudes_perday = grouped_birdday.altitude.mean()

eric = birddata.groupby('bird_name').get_group('Eric')
eric = eric.groupby('date')
sanne = birddata.groupby('bird_name').get_group('Sanne')
sanne = sanne.groupby('date')
nico = birddata.groupby('bird_name').get_group('Nico')
nico = nico.groupby('date')

eric_daily_speed  = eric.speed_2d.mean()
sanne_daily_speed = sanne.speed_2d.mean()
nico_daily_speed  = nico.speed_2d.mean()

plt.figure()
eric_daily_speed.plot(label="Eric")
sanne_daily_speed.plot(label="Sanne")
nico_daily_speed.plot(label="Nico")
plt.legend(loc="upper left")
plt.savefig("patterns.pdf")
