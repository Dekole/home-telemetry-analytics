# home-telemetry-analytics

## Project Overview

A home telemetry system that streams data from a TP-Link TCB72 camera to a home PC and builds applications on top of that data. The goal is to move beyond the Tapo app and build custom, programmable access to the camera feed and events.

## Camera Hardware

- **Model**: TP-Link TCB72 (Tapo-branded, Pan/Tilt, 2K QHD, 4MP)
- **Protocols confirmed supported**: RTSP (port 554), ONVIF Profile S (port 2020)
- **No official developer API** from TP-Link

## Connectivity

### RTSP Stream
- Main stream (high quality): `rtsp://<username>:<password>@<camera_ip>:554/stream1`
- Sub stream (lower res): `rtsp://<username>:<password>@<camera_ip>:554/stream2`
- Requires a **camera account** created in the Tapo app (separate from Tapo login credentials): Settings > Advanced Settings > Camera Account
- Max 2 simultaneous RTSP streams
- **Third-Party Compatibility must be enabled**: Tapo App > Me > Tapo Lab > Third-Party Compatibility > On

### ONVIF
- Port: 2020
- Profile S
- Enables motion events, PTZ control (pan/tilt supported on TCB72)
- Does not work simultaneously with SD card + Tapo Care (pick two of the three)

### pytapo (Unofficial Python Library)
- Repo: https://github.com/JurajNyiri/pytapo
- Reverse-engineered Tapo protocol; no official API backing
- TCB72 is **not explicitly listed** in confirmed supported models
- Confirmed models are C-series and TC-series cameras
- Likely compatible since TCB72 is Tapo-based, but treat as unverified until tested
- Provides: camera controls, motion event queries, PTZ, SD card recording downloads, privacy mode, reboot

## Development Setup

- **Planning machine**: Windows PC, Cowork (Claude desktop app), working directory at `C:\Peter\projects\home-telemetry-analytics`
- **Development machine**: Separate computer running Claude Code CLI
- **Repo**: https://github.com/Dekole/home-telemetry-analytics
- **Workflow**: Plan and document here, commit, pull and implement on dev machine via Claude Code

## Key Constraints and Notes

- RTSP is the primary, reliable path for streaming video frames to the PC
- ONVIF gives camera control and motion events beyond what RTSP provides
- pytapo adds programmatic camera control but is unofficial and may break on firmware updates
- SD card + Tapo Care + ONVIF/NVR cannot all run simultaneously; pick two
- Tapo cameras expect API messages in sequential order; parallel calls cause auth errors

## Status

- [ ] Camera connected to local network
- [ ] Camera account created in Tapo app
- [ ] Third-Party Compatibility enabled
- [ ] RTSP stream verified (e.g., via VLC)
- [ ] ONVIF connectivity verified
- [ ] pytapo compatibility with TCB72 tested
- [ ] Application architecture defined
