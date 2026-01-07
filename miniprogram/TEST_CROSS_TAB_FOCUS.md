# Cross-Tab Focus Feature Test Guide

## Overview
This document describes the **cross-tab focus feature** that automatically switches from the Plan page to the Map page and focuses on the corresponding POI when the ARRIVE button is clicked.

## Feature Description

When a user clicks the **ARRIVE** button on a stop in the Plan page:
1. The backend API is called to mark the stop as "ARRIVED"
2. A `pending_focus` instruction is saved to WeChat storage
3. The app automatically switches to the Map tab (using `wx.switchTab`)
4. The Map page reads the `pending_focus` instruction in `onShow`
5. The Map page:
   - Switches to `browse` mode (card deck visible)
   - Scrolls the card deck to the corresponding POI card
   - Centers and zooms the map to the POI location (zoom level 16)
   - Displays a toast message: "已到达 [POI Name]"
6. The `pending_focus` instruction is cleared to prevent duplicate triggers

## Implementation Details

### Plan Page (`miniprogram/pages/plan/index.js`)

**Function: `arriveStop(e)`**
```javascript
arriveStop(e) {
    const stopId = e.currentTarget.dataset.stopId;
    const tripId = this.data.tripId;
    
    // Call backend API: POST /api/trips/{tripId}/stops/{stopId}/arrive
    wx.request({
        url: `${API_BASE_URL}/api/trips/${tripId}/stops/${stopId}/arrive`,
        method: 'POST',
        success: (res) => {
            if (res.statusCode >= 200 && res.statusCode < 300) {
                // Refresh trip data
                this.fetchTrip();
                
                // Save cross-tab focus instruction
                wx.setStorageSync('pending_focus', {
                    tripId: tripId,
                    stopId: stopId,
                    action: 'ARRIVE',
                    ts: Date.now()
                });
                
                // Switch to Map tab after 500ms
                setTimeout(() => {
                    wx.switchTab({
                        url: '/pages/map/index'
                    });
                }, 500);
            }
        }
    });
}
```

### Map Page (`miniprogram/pages/map/index.js`)

**Function: `onShow()`**
```javascript
onShow() {
    console.log('[Map onShow] Map 页面显示');
    
    // Update tabBar selection
    if (typeof this.getTabBar === 'function' && this.getTabBar()) {
        this.getTabBar().setData({ selected: 1 });
    }
    
    // Apply pending focus instruction
    this.applyPendingFocus();
}
```

**Function: `applyPendingFocus()`**
```javascript
applyPendingFocus() {
    const pendingFocus = wx.getStorageSync('pending_focus');
    
    if (!pendingFocus) return;
    
    console.log('[applyPendingFocus] 检测到聚焦指令:', pendingFocus);
    
    // Validate timestamp (ignore if older than 30 seconds)
    const now = Date.now();
    if (now - pendingFocus.ts > 30000) {
        console.log('[applyPendingFocus] 指令已过期，忽略');
        wx.removeStorageSync('pending_focus');
        return;
    }
    
    // Check if tripId matches
    if (pendingFocus.tripId !== this.data.tripId) {
        // Load the correct trip first
        this.fetchTrip(pendingFocus.tripId).then(() => {
            this.focusToStop(pendingFocus.stopId);
        });
    } else {
        // Directly focus to the stop
        this.focusToStop(pendingFocus.stopId);
    }
    
    // Clear focus instruction (prevent duplicate triggers)
    wx.removeStorageSync('pending_focus');
}
```

**Function: `focusToStop(stopId)`**
```javascript
focusToStop(stopId) {
    const { attractions } = this.data;
    
    // Find the corresponding attraction index
    const idx = attractions.findIndex(a => a.stopId === stopId || a.id === stopId);
    
    if (idx < 0) {
        console.warn('[focusToStop] ⚠️ 未找到对应的 attraction:', stopId);
        return;
    }
    
    const targetAttraction = attractions[idx];
    
    // Switch to browse mode and set activeCardIndex
    this.setData({
        viewMode: 'browse',
        activeCardIndex: idx,
        selectedAttraction: targetAttraction
    }, () => {
        // Update card styles to center the target card
        this.updateCardStyles();
        
        // Move map center to the POI
        if (targetAttraction.latitude && targetAttraction.longitude) {
            const mapCtx = wx.createMapContext('tripMap', this);
            mapCtx.moveToLocation({
                latitude: targetAttraction.latitude,
                longitude: targetAttraction.longitude,
                success: () => {
                    // Set zoom level to 16 (can see buildings clearly)
                    this.setData({
                        latitude: targetAttraction.latitude,
                        longitude: targetAttraction.longitude,
                        scale: 16
                    });
                }
            });
        }
        
        // Show toast message
        wx.showToast({
            title: `已到达 ${targetAttraction.name}`,
            icon: 'success',
            duration: 2000
        });
    });
}
```

## Testing Steps

### Prerequisites
1. Ensure backend is running: `cd bakend && python main.py`
2. Ensure at least one trip with multiple stops exists in the database
3. Ensure stops have valid `lat` and `lon` coordinates (from backend API)

### Test Case 1: Basic Cross-Tab Focus
1. Open the mini program in WeChat DevTools
2. Navigate to the **Plan** page
3. Verify that stops are displayed with their status
4. Click the **ARRIVE** button on any stop (preferably the first or second one)
5. **Expected Results:**
   - A loading indicator appears ("更新中...")
   - After success, a toast shows "已标记到达"
   - The app automatically switches to the **Map** tab
   - The Map page opens in `browse` mode (card deck visible)
   - The card deck scrolls to the corresponding POI card (centered)
   - The map centers and zooms to the POI location (zoom level 16)
   - A toast shows "已到达 [POI Name]"
   - The map displays the marker at the correct location

### Test Case 2: Verify No Infinite Loop
1. Complete Test Case 1
2. Manually switch back to the **Plan** page (click Plan tab)
3. Switch back to the **Map** page (click Map tab)
4. **Expected Results:**
   - The Map page displays normally
   - No automatic focus occurs (because `pending_focus` was already cleared)
   - No toast message appears
   - The map remains at the last state (not re-centered)

### Test Case 3: Multiple ARRIVE Actions
1. On the **Plan** page, click **ARRIVE** on the first stop
2. Wait for the Map page to focus on the first stop
3. Switch back to the **Plan** page
4. Click **ARRIVE** on the second stop
5. **Expected Results:**
   - Each ARRIVE action triggers a new cross-tab focus
   - The Map page correctly focuses on the second stop (not the first)
   - The card deck and map center update to the second stop

### Test Case 4: Expired Focus Instruction
1. On the **Plan** page, click **ARRIVE** on a stop
2. **Do not** switch to the Map page immediately
3. Wait for 35 seconds (longer than the 30-second timeout)
4. Manually switch to the **Map** page
5. **Expected Results:**
   - No automatic focus occurs (instruction expired)
   - No toast message appears
   - The Map page displays in its default state

### Test Case 5: Different Trip IDs
1. Create or load a second trip (different `tripId`)
2. On the **Plan** page of the first trip, click **ARRIVE**
3. Before the Map page loads, switch the app's context to the second trip
4. **Expected Results:**
   - The Map page detects the `tripId` mismatch
   - The Map page loads the correct trip data (from `pending_focus.tripId`)
   - The Map page focuses on the correct stop

## Debugging Tips

### Check Console Logs
Enable the WeChat DevTools console and filter for:
- `[arriveStop]` - Plan page ARRIVE button logic
- `[applyPendingFocus]` - Map page focus instruction processing
- `[focusToStop]` - Map page focus logic
- `[drawMarkers]` - Marker generation and coordinate validation

### Verify Storage
Use WeChat DevTools **Storage** panel to check:
- `pending_focus`: Should contain `{tripId, stopId, action, ts}` after ARRIVE is clicked
- `pending_focus`: Should be cleared after the Map page reads it
- `last_trip_id`: Should match the current trip ID

### Check Backend Response
Use WeChat DevTools **Network** panel to verify:
- `POST /api/trips/{tripId}/stops/{stopId}/arrive` returns 200 OK
- `GET /api/trips/{tripId}` returns stops with `lat` and `lon` fields

### Common Issues and Solutions

| Issue | Possible Cause | Solution |
|-------|---------------|----------|
| Map doesn't auto-switch after ARRIVE | `wx.switchTab` failed | Check console for errors; verify Map page is in `app.json` tabBar |
| Map doesn't focus on POI | `pending_focus` not saved | Check `arriveStop` logic; verify storage write |
| Map focuses but doesn't zoom | Invalid coordinates | Check backend response; verify `stop.lat` and `stop.lon` |
| Infinite focus loop | `pending_focus` not cleared | Check `applyPendingFocus` logic; verify storage clear |
| Map centers but card doesn't scroll | `activeCardIndex` not set | Check `focusToStop` logic; verify `updateCardStyles` call |

## Performance Considerations

- **Storage Size**: `pending_focus` is small (~100 bytes), cleared after use
- **Memory**: No memory leaks; focus instruction is one-time use
- **Battery**: Map operations (center, zoom) are native and efficient
- **Network**: Only two API calls (POST arrive, GET trip refresh)

## Future Enhancements

1. **Smooth Animation**: Add smooth scroll animation for card deck
2. **Custom Zoom Level**: Allow users to configure preferred zoom level
3. **Multi-Stop Focus**: Support focusing on multiple stops in sequence
4. **Focus History**: Track focus history for analytics
5. **Accessibility**: Add voice announcements for visually impaired users

## Related Files

- `miniprogram/pages/plan/index.js` - Plan page (ARRIVE button logic)
- `miniprogram/pages/plan/index.wxml` - Plan page UI (ARRIVE button)
- `miniprogram/pages/map/index.js` - Map page (focus logic)
- `miniprogram/pages/map/index.wxml` - Map page UI (map and cards)
- `bakend/app/api/trips.py` - Backend API (arrive endpoint)
- `bakend/app/services/mock_db.py` - Mock database (POI coordinates)

## Conclusion

The cross-tab focus feature provides a seamless user experience by automatically navigating to the Map page and highlighting the POI when ARRIVE is clicked. The implementation uses WeChat's storage API to pass instructions between tabs, with proper validation and cleanup to prevent duplicate triggers or infinite loops.

---

**Last Updated**: 2025-01-17
**Author**: GitHub Copilot
**Status**: ✅ Implemented and Ready for Testing
