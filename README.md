# Kronoterm Heat Pump (Local) — Home Assistant integration

Local, cloud-free Home Assistant control for Kronoterm heat pumps with the
**TERMOTRONIC 3000 / TTEH-WEB** web module (e.g. Hydro S, Adapt, Versi with the
Wi-Fi/LAN web module).

Unlike cloud-based integrations, this one talks **only on your LAN** to a small
*local cloud emulator* that impersonates the Kronoterm cloud endpoint
(`wd.elektrina.si`). The heat pump module connects to it exactly like it would
to the real cloud (SSLv3 WebSocket), so you get the **full register set** —
including live power, COP and every setpoint — with no cloud account, no
polling limits and no internet dependency.

```
Heat pump module ──WSS──▶ local cloud emulator ──HTTP──▶ this integration ──▶ Home Assistant
                          (any always-on Linux box)
```

## Prerequisites

1. A Kronoterm heat pump with a TTEH-WEB module on your LAN.
2. The **local cloud emulator** running somewhere always-on (a Proxmox LXC, a
   Raspberry Pi, any Linux box with Python ≤ 3.11):
   see the emulator repository for setup — it is a single dependency-free
   Python service plus one DNS override on your router pointing
   `wd.elektrina.si` at it.
3. Home Assistant 2024.6 or newer.

> The Kronoterm cloud service is not required and the official cloud app will
> show the heat pump as offline while the emulator is in use. Reverting to the
> stock cloud is a one-line DNS change.

## Installation

### HACS (recommended)

1. HACS → ⋮ → **Custom repositories** → add this repository URL, type **Integration**.
2. Install **Kronoterm Heat Pump (Local)**.
3. Restart Home Assistant.
4. **Settings → Devices & services → Add integration → Kronoterm Heat Pump (Local)**
   and enter the emulator host/port (default port `8099`).

### Manual

Copy `custom_components/kronoterm` into your HA `config/custom_components/`
directory, restart Home Assistant, then add the integration as above.

## Entities

One device: **Kronoterm Heat Pump** (serial = module UID).

| Platform | Entities |
|---|---|
| Climate | One per active heating/cooling loop (target temperature, off/normal/schedule, heating/cooling/idle action) |
| Water heater | Domestic hot water: current/target temperature, off/normal/schedule mode |
| Sensors | Outside/DHW/HP outlet temperature, electrical power (W), thermal capacity (W), COP, SCOP, electrical & thermal energy (kWh), system pressure, heat pump load, working function, operation regime/program, error status, loop temperatures |
| Binary sensors | Compressor, defrost, problem, DHW circulation, main pump, loop pumps, module connectivity |
| Switches | System on/off, vacation mode, thermal disinfection (anti-legionella), DHW circulation pump |
| Select | Operation program (normal / eco / comfort) |
| Number | System temperature correction |

Undocumented/experimental registers (theoretical COP & power, load %, fan
speed, extra energy counters) are created **disabled by default** — enable them
from the entity registry if you want to explore. Entities for heating loops
that don't exist on your system are not created at all (reload the integration
if your hardware configuration changes).

Writes go straight to the heat pump controller over the live module connection
and are reflected back within one poll interval (15 s).

## How it works (short version)

The TTEH-WEB module maintains a persistent WebSocket over SSLv3 to the vendor
cloud. The emulator terminates that connection locally (the module does not
pin the cloud CA), speaks the vendor framing protocol, mirrors the full
register set, and exposes it over a small HTTP API that this integration
polls. No Modbus wiring, no heat pump configuration changes.

## Disclaimer

Not affiliated with Kronoterm d.o.o. Reverse-engineered for interoperability.
Use at your own risk; writing registers changes how your heat pump operates.
