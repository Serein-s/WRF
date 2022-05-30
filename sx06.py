import numpy as np
import cmaps
import cartopy.crs as ccrs
import matplotlib.ticker as mticker
import cartopy.feature as cfeature
from cartopy.io.shapereader import Reader
import matplotlib
import matplotlib.pyplot as plt
from netCDF4 import Dataset
from wrf import (getvar, interplevel, to_np, latlon_coords, get_cartopy,
                 cartopy_xlim, cartopy_ylim)
#防止中文出错
matplotlib.rcParams['font.family'] = 'sans-serif'
matplotlib.rcParams['font.sans-serif'] = ['KaiTi']
plt.rcParams['axes.unicode_minus'] = False

ncfile = Dataset(r"D:\data\data\wrf\sx06\wrfout_d01_2021-07-20_12_00_00")
new_ncfile = Dataset(
    r"D:\data\data\wrf\sx06\new_wrfout_d01_2021-07-20_12_00_00")


def lbt_scale(ax, z):
    # Set the map bounds
    ax.set_xlim(cartopy_xlim(z))
    ax.set_ylim(cartopy_ylim(z))
    ax.add_feature(cfeature.COASTLINE.with_scale('50m'))
    lb = ax.gridlines(draw_labels=True,
                      x_inline=False,
                      y_inline=False,
                      linewidth=0.5,
                      color='gray',
                      alpha=0.8,
                      linestyle='--')
    lb.top_labels = False
    lb.right_labels = None
    lb.xlocator = mticker.FixedLocator(range(105, 130, 5))
    lb.ylabel_style = {'size': 12, 'color': 'k'}
    lb.xlabel_style = {'size': 12, 'color': 'k'}
    lb.rotate_labels = False
    ax.add_geometries(Reader(r"D:\data\map\bou2_4l.shp").geometries(),
                      ccrs.PlateCarree(),
                      facecolor='none',
                      edgecolor='k',
                      linewidth=0.7)
    ax.add_geometries(Reader(r"D:\data\china_map\river1.shp").geometries(),
                      ccrs.PlateCarree(),
                      facecolor='none',
                      edgecolor='b',
                      linewidth=0.7)


def draw_wrf_rh_ht_uv(ncfile, level, figsize, title_number=None):
    p = getvar(ncfile, "pressure")
    z = getvar(ncfile, "z")
    ht_850 = interplevel(z, p, level)
    lats, lons = latlon_coords(ht_850)
    ua = getvar(ncfile, "ua")
    va = getvar(ncfile, "va")
    rh = getvar(ncfile, "rh")
    u_850 = interplevel(ua, p, level)
    v_850 = interplevel(va, p, level)
    rh_850 = interplevel(rh, p, level)

    cart_proj = get_cartopy(ht_850)
    fig = plt.figure(figsize=figsize)
    ax = fig.add_subplot(111, projection=cart_proj)

    c11 = ax.contourf(to_np(lons),
                      to_np(lats),
                      to_np(rh_850),
                      levels=np.arange(60, 101, 10),
                      cmap=cmaps.cmocean_algae,
                      transform=ccrs.PlateCarree(),
                      extend='both')
    ax.contour(to_np(lons),
               to_np(lats),
               to_np(ht_850),
               levels=20,
               colors="black",
               transform=ccrs.PlateCarree())
    #plt.clabel(contours, inline=1, fontsize=10, fmt="%i")

    ax.barbs(to_np(lons),
             to_np(lats),
             to_np(u_850),
             to_np(v_850),
             regrid_shape=15,
             transform=ccrs.PlateCarree(),
             length=6)
    cbar = plt.colorbar(c11, shrink=0.55, pad=0.06, orientation='horizontal')
    cbar.ax.tick_params(labelsize=12, direction='in')
    cbar.set_ticks(np.arange(60, 101, 10))

    # Set the map bounds
    lbt_scale(ax, z)

    ax.set_title(title_number, loc='left', fontsize=15)
    ax.set_title('相对湿度RH 单位:%  {}'.format(rh_850.Time.values),
                 loc='right',
                 fontsize=15)
    plt.tight_layout()


def draw_wrf_vapor_ht_uv(ncfile, level, figsize, title_number=None):
    w = getvar(ncfile, "QVAPOR")
    p = getvar(ncfile, "pressure")
    w_850 = interplevel(w, p, level)
    z = getvar(ncfile, "z")
    ht_850 = interplevel(z, p, level)
    ua = getvar(ncfile, "ua")
    va = getvar(ncfile, "va")
    u_850 = interplevel(ua, p, level)
    v_850 = interplevel(va, p, level)
    lats, lons = latlon_coords(w)
    cart_proj = get_cartopy(w)
    q_850 = w_850 / (1 + w_850)
    qq = ((np.sqrt(u_850**2 + v_850**2)) * q_850) / 9.8 * 1000
    fig = plt.figure(figsize=figsize)
    ax = fig.add_subplot(111, projection=cart_proj)
    ax.contour(to_np(lons),
               to_np(lats),
               to_np(ht_850),
               levels=20,
               colors="black",
               zorder=1,
               transform=ccrs.PlateCarree())
    plt.barbs(to_np(lons),
              to_np(lats),
              to_np(u_850),
              to_np(v_850),
              regrid_shape=15,
              zorder=2,
              transform=ccrs.PlateCarree(),
              length=6)
    c11 = ax.contourf(to_np(lons),
                      to_np(lats),
                      to_np(qq),
                      levels=np.arange(0, 61, 10),
                      cmap=cmaps.MPL_BuGn,
                      zorder=0,
                      transform=ccrs.PlateCarree(),
                      extend='both')

    cbar = plt.colorbar(c11, shrink=0.6, pad=0.06, orientation='horizontal')
    cbar.ax.tick_params(labelsize=12, direction='in')
    cbar.set_ticks(np.arange(0, 61, 10))

    # Set the map bounds
    lbt_scale(ax, z)
    ax.set_title(title_number, loc='left', fontsize=15)
    ax.set_title('水汽通量单位: g/(cm*hPa*s) {}'.format(w.Time.values),
                 loc='right',
                 fontsize=15)
    plt.tight_layout()


def cal_all_prec(ncfile):
    # 累计总积云对流降水量
    pre_1 = getvar(ncfile, "RAINC")
    # 累计总格点降水量
    pre_2 = getvar(ncfile, "RAINNC")
    #总降水量
    pre_all = pre_1 + pre_2
    return pre_all


pre_all = cal_all_prec(ncfile)
new_pre_all = cal_all_prec(new_ncfile)
pre_diff = new_pre_all - pre_all
z = getvar(ncfile, "z")
cart_proj = get_cartopy(z)
lats, lons = latlon_coords(z)
fig = plt.figure(figsize=(12, 9))
ax = fig.add_subplot(111, projection=cart_proj)
c11 = ax.contourf(to_np(lons),
                  to_np(lats),
                  to_np(pre_diff),
                  levels=np.arange(-15, 101, 5),
                  cmap=cmaps.prcp_1,
                  transform=ccrs.PlateCarree(),
                  extend='both')

cbar = plt.colorbar(c11, shrink=0.6, pad=0.06, orientation='horizontal')
cbar.ax.tick_params(labelsize=12, direction='in')
cbar.set_ticks(np.arange(-15, 101, 10))
lbt_scale(ax, z)

ax.set_title('(e)', loc='left', fontsize=15)
ax.set_title('两种方案 12小时累计降水量之差  单位：mm', fontsize=15)
plt.tight_layout()
plt.savefig(r"D:\data\data\wrf\sx06\prec_diff.jpg",
            dpi=300,
            bbox_inches='tight')

draw_wrf_rh_ht_uv(ncfile, 850, [12, 9], '(a) old 方案')
plt.savefig(r"D:\data\data\wrf\sx06\rh.jpg", dpi=300, bbox_inches='tight')
draw_wrf_rh_ht_uv(new_ncfile, 850, [12, 9], '(b) new 方案')
plt.savefig(r"D:\data\data\wrf\sx06\rh_new.jpg", dpi=300, bbox_inches='tight')
draw_wrf_vapor_ht_uv(ncfile, 850, [12, 9], '(c) old 方案')
plt.savefig(r"D:\data\data\wrf\sx06\water_vapor.jpg",
            dpi=300,
            bbox_inches='tight')
draw_wrf_vapor_ht_uv(new_ncfile, 850, [12, 9], '(d) old 方案')
plt.savefig(r"D:\data\data\wrf\sx06\new_water_vapor.jpg",
            dpi=300,
            bbox_inches='tight')
plt.show()
