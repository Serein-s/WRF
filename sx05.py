from netCDF4 import Dataset
from wrf import getvar
import matplotlib.ticker as mticker
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.io.shapereader import Reader
import cmaps
import matplotlib
#防止中文出错
matplotlib.rcParams['font.family'] = 'sans-serif'
matplotlib.rcParams['font.sans-serif'] = ['KaiTi']
plt.rcParams['axes.unicode_minus'] = False
ncfile = Dataset(r"D:\data\data\wrf\sx05\wrfout_d01_2021-07-20_18_00_00")
# 累计总积云对流降水量
pre_1 = getvar(ncfile, "RAINC")
# 累计总格点降水量
pre_2 = getvar(ncfile, "RAINNC")
#总降水量
pre_all = pre_1 + pre_2

lat = getvar(ncfile, 'lat')
lon = getvar(ncfile, 'lon')

#地形高度
hgt = getvar(ncfile, 'HGT')


def LBT_map(ax, lon, lat, data, cmap, lev):

    ax.set_extent([108.3, 127.6, 23.8, 39.26], ccrs.PlateCarree())
    ax.add_feature(cfeature.COASTLINE, lw=0.3)
    ax.add_feature(cfeature.LAKES.with_scale('50m'))
    ax.add_geometries(Reader(r"D:\data\china_map\river1.shp").geometries(),
                      ccrs.PlateCarree(),
                      facecolor='none',
                      edgecolor='b',
                      linewidth=0.5)
    ax.add_geometries(Reader(r'D:\data\china_map\china1.shp').geometries(),
                      ccrs.PlateCarree(),
                      facecolor='none',
                      edgecolor='k',
                      linewidth=0.5)
    ax.add_geometries(Reader(r"D:\data\map\bou2_4l.shp").geometries(),
                      ccrs.PlateCarree(),
                      facecolor='none',
                      edgecolor='k',
                      linewidth=0.7)
    ax.add_geometries(
        Reader(r'D:\data\china_map\ne_10m_land.shp').geometries(),
        ccrs.PlateCarree(),
        facecolor='none',
        edgecolor='k',
        linewidth=0.5)
    ax.add_geometries(
        Reader(r'D:\data\china_map\ne_50m_lakes.shp').geometries(),
        ccrs.PlateCarree(),
        facecolor='none',
        edgecolor='k',
        linewidth=0.5)
    lb = ax.gridlines(draw_labels=None,
                      x_inline=False,
                      y_inline=False,
                      linewidth=0.5,
                      color='gray',
                      alpha=0.8,
                      linestyle='--')
    lb.xlocator = mticker.FixedLocator(range(0, 180, 10))
    lb.ylocator = mticker.FixedLocator(range(0, 90, 10))

    lb = ax.gridlines(draw_labels=True,
                      x_inline=False,
                      y_inline=False,
                      linewidth=0.5,
                      color='gray',
                      alpha=0.8,
                      linestyle='--')
    lb.top_labels = False
    lb.right_labels = None
    lb.xlocator = mticker.FixedLocator(range(105, 140, 5))
    lb.ylocator = mticker.FixedLocator(range(24, 40, 2))
    lb.ylabel_style = {'size': 12, 'color': 'k'}
    lb.xlabel_style = {'size': 12, 'color': 'k'}
    lb.rotate_labels = False

    c11 = ax.contourf(lon,
                      lat,
                      data,
                      cmap=cmap,
                      levels=lev,
                      zorder=0,
                      transform=ccrs.PlateCarree(),
                      extend='both')
    cbar = plt.colorbar(c11, shrink=0.9, pad=0.06, orientation='horizontal')
    cbar.ax.tick_params(labelsize=12, direction='in')


fig = plt.figure(figsize=(12, 8))
map = ccrs.LambertConformal(central_longitude=118, central_latitude=32)
ax1 = fig.add_subplot(1, 2, 1, projection=map)
lev_pre = np.arange(0, 72, 5)
LBT_map(ax1, lon, lat, pre_all, cmaps.prcp_1, lev_pre)
ax1.set_title('总降水量分布', fontsize=15)
ax1.set_title('(a)', loc='left', fontsize=15)

ax2 = fig.add_subplot(1, 2, 2, projection=map)
lev_hgt = np.arange(0, 2005, 200)
LBT_map(ax2, lon, lat, hgt, cmaps.NCV_jaisnd, lev_hgt)
ax2.set_title('地形图', fontsize=15)
ax2.set_title('(b)', loc='left', fontsize=15)

plt.tight_layout(pad=0.5, w_pad=10, h_pad=2)
plt.savefig(r"D:\data\data\wrf\sx05\pre.jpg", dpi=300, bbox_inches='tight')
plt.show()
