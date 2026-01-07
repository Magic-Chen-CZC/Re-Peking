/**
 * GPS 地理位置工具函数
 * 用于计算距离、判断围栏等
 */

/**
 * 使用 Haversine 公式计算两点间的距离（米）
 * @param {number} lat1 - 点1纬度
 * @param {number} lon1 - 点1经度
 * @param {number} lat2 - 点2纬度
 * @param {number} lon2 - 点2经度
 * @returns {number} 距离（米）
 */
function haversineDistance(lat1, lon1, lat2, lon2) {
  const R = 6371000; // 地球半径（米）
  const φ1 = lat1 * Math.PI / 180;
  const φ2 = lat2 * Math.PI / 180;
  const Δφ = (lat2 - lat1) * Math.PI / 180;
  const Δλ = (lon2 - lon1) * Math.PI / 180;

  const a = Math.sin(Δφ / 2) * Math.sin(Δφ / 2) +
            Math.cos(φ1) * Math.cos(φ2) *
            Math.sin(Δλ / 2) * Math.sin(Δλ / 2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));

  return R * c; // 返回米
}

/**
 * 从 stop 对象中提取坐标
 * 兼容多种字段命名方式
 * @param {Object} stop - 站点对象
 * @returns {Object|null} {lat, lon} 或 null（如果没有坐标）
 */
function extractStopCoordinates(stop) {
  if (!stop) return null;

  let lat = null;
  let lon = null;

  // 🔥 优先级1: 直接字段 lat/lon
  if (stop.lat != null && stop.lon != null) {
    lat = stop.lat;
    lon = stop.lon;
  }
  // 🔥 优先级2: 直接字段 latitude/longitude
  else if (stop.latitude != null && stop.longitude != null) {
    lat = stop.latitude;
    lon = stop.longitude;
  }
  // 🔥 优先级3: location 对象 (lat/lng) - 重点支持 lng 字段
  else if (stop.location) {
    if (stop.location.lat != null && stop.location.lng != null) {
      lat = stop.location.lat;
      lon = stop.location.lng;
    }
    // location 对象 (lat/lon)
    else if (stop.location.lat != null && stop.location.lon != null) {
      lat = stop.location.lat;
      lon = stop.location.lon;
    }
    // location 对象 (latitude/longitude)
    else if (stop.location.latitude != null && stop.location.longitude != null) {
      lat = stop.location.latitude;
      lon = stop.location.longitude;
    }
  }
  // 🔥 优先级4: coords 对象 (lat/lon)
  else if (stop.coords) {
    if (stop.coords.lat != null && stop.coords.lon != null) {
      lat = stop.coords.lat;
      lon = stop.coords.lon;
    }
    // coords 对象 (latitude/longitude)
    else if (stop.coords.latitude != null && stop.coords.longitude != null) {
      lat = stop.coords.latitude;
      lon = stop.coords.longitude;
    }
  }

  // 🔥 统一转换为数字（使用 Number 或 parseFloat）
  if (lat != null && lon != null) {
    lat = Number(lat);
    lon = Number(lon);
    
    // 🔥 排除 0,0 坐标（无效坐标）
    if (lat === 0 && lon === 0) {
      console.warn('[extractStopCoordinates] 坐标为 0,0，视为无效坐标');
      console.warn('[extractStopCoordinates] stop 详情:', {
        name: stop.name || stop._stopId || 'unknown',
        可见字段: Object.keys(stop),
        lat字段: stop.lat,
        lon字段: stop.lon,
        latitude字段: stop.latitude,
        longitude字段: stop.longitude,
        location字段: stop.location,
        coords字段: stop.coords
      });
      return null;
    }
    
    // 验证坐标有效性（北京大约在 39°N, 116°E）
    if (!isNaN(lat) && !isNaN(lon) && 
        lat > 0 && lat < 90 && 
        lon > 0 && lon < 180) {
      return { lat, lon };
    } else {
      console.warn('[extractStopCoordinates] 坐标超出合理范围:', { 
        name: stop.name || stop._stopId || 'unknown',
        lat, 
        lon 
      });
    }
  } else {
    // 没有找到任何坐标字段
    console.warn('[extractStopCoordinates] 未找到有效坐标字段');
    console.warn('[extractStopCoordinates] stop 详情:', {
      name: stop.name || stop._stopId || 'unknown',
      可见字段: Object.keys(stop),
      lat字段: stop.lat,
      lon字段: stop.lon,
      latitude字段: stop.latitude,
      longitude字段: stop.longitude,
      location字段: stop.location,
      coords字段: stop.coords
    });
  }

  return null;
}

/**
 * 获取当前目标站点（第一个未完成的站点）
 * @param {Array} stops - 站点列表
 * @returns {Object|null} 目标站点或 null
 */
function getCurrentTargetStop(stops) {
  if (!stops || !Array.isArray(stops) || stops.length === 0) {
    return null;
  }

  // 按 seq 或 _seq 排序，找到第一个未完成的
  const sorted = [...stops].sort((a, b) => {
    const seqA = a.seq || a._seq || 0;
    const seqB = b.seq || b._seq || 0;
    return seqA - seqB;
  });

  // 找到第一个不是 COMPLETED 的站点
  const target = sorted.find(stop => {
    const status = stop.status || stop._status || 'UPCOMING';
    return status !== 'COMPLETED';
  });

  return target || null;
}

/**
 * 获取离指定坐标最近的未完成站点
 * @param {Array} stops - 站点列表
 * @param {number} lat - 参考纬度
 * @param {number} lon - 参考经度
 * @returns {Object|null} 最近的未完成站点或 null
 */
function getNearestTargetStop(stops, lat, lon) {
  if (!stops || !Array.isArray(stops) || stops.length === 0) {
    console.warn('[getNearestTargetStop] stops 为空');
    return null;
  }

  if (isNaN(lat) || isNaN(lon)) {
    console.warn('[getNearestTargetStop] 参考坐标无效:', { lat, lon });
    return null;
  }

  // 过滤出未完成且有坐标的站点
  const unfinishedStops = stops.filter(stop => {
    const status = stop.status || stop._status || 'UPCOMING';
    // 只选择 UPCOMING 或 VISITING 状态的（排除 COMPLETED 和 SKIPPED）
    return status !== 'COMPLETED' && status !== 'SKIPPED';
  });

  if (unfinishedStops.length === 0) {
    console.warn('[getNearestTargetStop] 没有未完成的 stops');
    return null;
  }

  // 计算每个站点到参考坐标的距离
  let nearest = null;
  let minDistance = Infinity;

  for (const stop of unfinishedStops) {
    const coords = extractStopCoordinates(stop);
    if (!coords) {
      console.log('[getNearestTargetStop] 跳过无坐标的 stop:', stop.name || stop._stopId);
      continue;
    }

    const distance = haversineDistance(lat, lon, coords.lat, coords.lon);
    console.log('[getNearestTargetStop] 计算距离:', {
      stop: stop.name || stop._stopId,
      distance: `${distance.toFixed(1)}m`
    });

    if (distance < minDistance) {
      minDistance = distance;
      nearest = stop;
    }
  }

  if (nearest) {
    console.log('[getNearestTargetStop] ✅ 找到最近的 stop:', {
      name: nearest.name,
      stopId: nearest._stopId || nearest.id,
      distance: `${minDistance.toFixed(1)}m`
    });
  } else {
    console.warn('[getNearestTargetStop] ❌ 没有找到合适的 stop');
  }

  return nearest;
}

/**
 * 检查是否有定位权限
 * @returns {Promise<boolean>}
 */
function checkLocationPermission() {
  return new Promise((resolve) => {
    wx.getSetting({
      success: (res) => {
        const hasPermission = res.authSetting['scope.userLocation'];
        resolve(hasPermission !== false); // undefined 视为未询问，true 为已授权
      },
      fail: () => resolve(false)
    });
  });
}

/**
 * 请求定位权限
 * @returns {Promise<boolean>}
 */
function requestLocationPermission() {
  return new Promise((resolve) => {
    wx.authorize({
      scope: 'scope.userLocation',
      success: () => resolve(true),
      fail: () => {
        // 用户拒绝，引导去设置页
        wx.showModal({
          title: '需要定位权限',
          content: '开启定位权限后，可自动识别到达景点',
          confirmText: '去设置',
          success: (res) => {
            if (res.confirm) {
              wx.openSetting();
            }
          }
        });
        resolve(false);
      }
    });
  });
}

function normalizeCoords(location) {
  if (!location) return null;
  const lat = Number(location.lat != null ? location.lat : location.latitude);
  const lon = Number(location.lon != null ? location.lon : location.longitude);
  if (isNaN(lat) || isNaN(lon)) return null;
  return { lat, lon };
}

function orderByNearestNeighbor(points, startCoords) {
  const remaining = [...points];
  const ordered = [];
  let current = startCoords;

  while (remaining.length > 0) {
    let nearestIndex = 0;
    let minDistance = Infinity;

    remaining.forEach((point, index) => {
      const distance = haversineDistance(
        current.lat,
        current.lon,
        point.coords.lat,
        point.coords.lon
      );
      if (distance < minDistance) {
        minDistance = distance;
        nearestIndex = index;
      }
    });

    const next = remaining.splice(nearestIndex, 1)[0];
    ordered.push(next);
    current = next.coords;
  }

  return ordered;
}

function buildOptimizedRoute(items, userLocation) {
  if (!items || items.length <= 1) {
    return items || [];
  }

  const beijingCenter = { lat: 39.9087, lon: 116.3975 };
  const beijingRadiusKm = 80;
  const withCoords = [];
  const withoutCoords = [];

  items.forEach((item) => {
    const coords = extractStopCoordinates(item);
    if (coords) {
      withCoords.push({ item, coords });
    } else {
      withoutCoords.push(item);
    }
  });

  if (withCoords.length <= 1) {
    return [...items];
  }

  const userCoords = normalizeCoords(userLocation);
  const isUserInBeijing = userCoords
    ? haversineDistance(
        userCoords.lat,
        userCoords.lon,
        beijingCenter.lat,
        beijingCenter.lon
      ) <= beijingRadiusKm * 1000
    : false;
  let ordered;

  if (userCoords && isUserInBeijing) {
    ordered = orderByNearestNeighbor(withCoords, userCoords);
  } else {
    if (userCoords && !isUserInBeijing) {
      console.log('[buildOptimizedRoute] 用户不在北京范围内，忽略用户位置');
    }
    let bestRoute = null;
    let bestDistance = Infinity;

    for (let i = 0; i < withCoords.length; i++) {
      const start = withCoords[i];
      const remaining = withCoords.filter((_, idx) => idx !== i);
      const route = [start, ...orderByNearestNeighbor(remaining, start.coords)];
      let totalDistance = 0;

      for (let j = 0; j < route.length - 1; j++) {
        totalDistance += haversineDistance(
          route[j].coords.lat,
          route[j].coords.lon,
          route[j + 1].coords.lat,
          route[j + 1].coords.lon
        );
      }

      if (totalDistance < bestDistance) {
        bestDistance = totalDistance;
        bestRoute = route;
      }
    }

    ordered = bestRoute || withCoords;
  }

  const orderedItems = ordered.map((entry) => entry.item);
  return [...orderedItems, ...withoutCoords];
}

module.exports = {
  haversineDistance,
  extractStopCoordinates,
  getCurrentTargetStop,
  getNearestTargetStop,
  checkLocationPermission,
  requestLocationPermission,
  buildOptimizedRoute
};
