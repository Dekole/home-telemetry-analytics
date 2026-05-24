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
- **Risk**: Tapo firmware updates have historically broken pytapo (encryption protocol change in late 2024 is a documented example). Treat as supplemental layer only; ONVIF is the primary path for motion events and PTZ.

### MediaMTX (Protocol Bridge and Stream Server)
- Repo: https://github.com/bluenviron/mediamtx — open source, MIT license, free
- Official Docker image: `bluenviron/mediamtx`
- Ingests RTSP from the camera and re-serves as WebRTC (sub-second latency) or HLS (2-6s latency) to browsers
- Supports on-demand stream pulling: only connects to the camera when a client is actively consuming
- Handles file-based restreaming via ffmpeg (used for demo mode)
- **Must run with `--network=host` in Docker** — Docker's default bridged NAT changes UDP source ports, which breaks RTSP session tracking. This is documented by MediaMTX and is a Linux-only Docker feature; works correctly on headless Ubuntu.
- Acts as the single RTSP consumer from the camera, rebroadcasting internally to unlimited consumers, bypassing the camera's 2-stream limit

## Development Setup

- **Planning machine**: Windows PC, Cowork (Claude desktop app), working directory at `C:\Peter\projects\home-telemetry-analytics`
- **Development machine**: Separate computer running Claude Code CLI
- **Repo**: https://github.com/Dekole/home-telemetry-analytics
- **Workflow**: Plan and document here, commit, pull and implement on dev machine via Claude Code

## Key Constraints and Notes

- RTSP is the primary, reliable path for streaming video frames to the PC
- ONVIF gives camera control and motion events beyond what RTSP provides
- pytapo adds programmatic camera control but is unofficial and may break on firmware updates; use ONVIF as primary
- SD card + Tapo Care + ONVIF/NVR cannot all run simultaneously; pick two
- Tapo cameras expect API messages in sequential order; parallel calls cause auth errors
- Browsers cannot play RTSP natively; all browser video delivery must go through MediaMTX (WebRTC or HLS)
- Camera supports max 2 simultaneous RTSP streams; all internal consumers must connect via MediaMTX, not directly to the camera
- ONVIF WS-Discovery uses multicast and does not work from inside a bridged Docker container; connect to camera by direct IP instead
- ONVIF motion event reliability on Tapo cameras is variable; use pull-point subscriptions (not polling) as the primary approach, with polling as fallback
- Rolling 30-min buffer at 3-5 Mbps (stream copy, no re-encode) = ~700MB-1.1GB; use FFmpeg segment mode writing .mkv files with rotation logic; use stream1 if audio is required in the buffer
- On-demand stream pulling (MediaMTX feature): the RTSP connection to the camera should only be active when a client is consuming; this supports the requirement to not stream in the background when the app is idle. The event collector must use ONVIF directly (not RTSP) so it can run continuously without holding a stream open.

## Architecture Notes

These are confirmed decisions and findings from the risk/stack investigation session. The architecture discussion is ongoing in a separate session.

### Confirmed Stack Components
- **MediaMTX**: Core infrastructure service (not just demo mode). Single RTSP consumer from camera; rebroadcasts to browser via WebRTC/HLS. Runs in Docker with `--network=host`.
- **Backend**: FastAPI (Python) — natural fit given pytapo is Python and ONVIF libraries are Python-native.
- **Database**: PostgreSQL — implied by JSONB in event schema; correct choice.
- **Event collector**: Separate background service connecting to camera via ONVIF directly by IP (not via RTSP, not via WS-Discovery). Runs continuously.
- **Rolling buffer**: FFmpeg in segment mode, stream copy, .mkv output with rotation. Separate concern from the live viewer.
- **All services run in Docker Compose** on headless Ubuntu. Services needing camera network access use `--network=host`.

### In-Browser Video
- WebRTC via MediaMTX is the target (sub-second latency)
- HLS via MediaMTX is the fallback (2-6s latency, simpler to configure)

### On-Demand Streaming
- MediaMTX supports on-demand RTSP pulling (only connects to camera when a browser client is active)
- Event collector uses ONVIF independently and does not hold an RTSP stream open
- This satisfies the requirement to not stream in the background when no user is present

## UI Design

Reference mockup: `ui-mockup.html` in the repo root. Open in a browser for a live preview.

### Layout
- Single-page application — no navigation, everything on one screen.
- Two-column layout: video panel + PTZ controls (left), event log (right, fixed ~280px wide).
- Header: app name, device name, connection status badge (Live/Offline), demo mode indicator.

### Header
- Connection status shown as a colored pill badge (green = Live, appropriate color for Offline).
- When `DEMO_MODE=true`, a "Demo mode" badge is visible in the header at all times.

### Video Panel
- Video occupies the full left column width above the PTZ controls.
- Overlay (bottom-left): stream protocol and resolution label (e.g., `WebRTC · stream1 · 2K`).
- Overlay (bottom-right): live wall clock (HH:MM:SS).
- Overlay (top-right): mute/unmute toggle button. Default state: muted.

### PTZ Controls
- D-pad grid: up, down, left, right arrow buttons plus a center home-position button.
- Sits directly below the video panel, left-aligned.

### Event Log
- Displays all historical events from the database (not session-scoped).
- Filter chips at top: All, Motion, Person. Default: All.
- CSV export button exports the currently filtered set.
- Each row is a single line: colored dot indicator + full timestamp (`YYYY-MM-DD HH:MM:SS` in monospace) + event type badge.
- Event type colors: Person = blue, Motion = amber.
- Footer shows total event count for the active filter.

## Application Requirements

### Core (Current)

1. Application shall be hosted on a headless Ubuntu server, running in Docker containers.
2. The application supports a single camera instance.
3. The application shall include a background event collector service that runs continuously, polling ONVIF/pytapo for motion events and camera state changes, and logging them to a database.
4. The application shall include a stream viewer that displays live video and audio from the camera via RTSP. Audio shall be muted by default, with a mute/unmute toggle overlaid on the video panel. No fullscreen toggle is required.
5. The event log shall store all captured events with the following schema: `event_id` (PK), `timestamp`, `device_id`, `event_type`, `details` (JSON/JSONB).
6. The application shall provide a web UI, accessible from another computer on the network, that displays the full historical event log (all events ever recorded, not session-scoped). The event log shall support filtering by event type (e.g., All / Motion / Person) and CSV export of the visible filtered set. Each row displays timestamp (full date and time, `YYYY-MM-DD HH:MM:SS`) and event type as a color-coded badge, one row per event.
7. The application shall allow manual pan/tilt control of the camera via the web UI using a D-pad style control (up, down, left, right) with a center button to return the camera to its home position.
8. The application shall include a demo mode, configurable via an environment variable (e.g., `DEMO_MODE=true`), that substitutes a pre-recorded RTSP stream (served via MediaMTX) and mocks ONVIF responses, making the full application demonstrable without a physical camera.

### Near-Future

9. The application shall maintain a rolling 30-minute recording buffer of the camera stream, written to disk.

### Future

10. The application shall support automated pan/tilt control.
11. The application shall support analysis and visualization of captured event data.

## Status

- [ ] Camera connected to local network
- [ ] Camera account created in Tapo app
- [ ] Third-Party Compatibility enabled
- [ ] RTSP stream verified (e.g., via VLC)
- [ ] ONVIF connectivity verified
- [ ] pytapo compatibility with TCB72 tested
- [ ] Application architecture defined
