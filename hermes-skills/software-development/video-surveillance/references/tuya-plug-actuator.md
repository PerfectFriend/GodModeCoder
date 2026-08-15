# Tuya smart plug as actuator (Nivian NVS-SOCKETF-W2) — 2026-08

Client-chosen control element for SuperGuard floodlight/siren: a **Nivian NVS-SOCKETF-W2**
smart WiFi plug (EU Type F). Replaces (or augments) the ESP32 GPIO actuator.

## Hardware facts (verified from nivianhome.com product page)

- Brand: Nivian (nivianhome.com — Spanish security/smart-home vendor).
- Model: **NVS-SOCKETF-W2** (W2 is the current revision; plain NVS-SOCKETF-W is older).
- Radio: WiFi 2.4 GHz only (IEEE 802.11 b/g/n) — **cannot join 5 GHz SSID**; when configuring,
  connect the phone to the 2.4 GHz band (or temporarily disable 5 GHz) or pairing fails.
- Ratings: 3680 W max / 16 A, 100–250 V AC, Type F (Schuko/EU).
- Ecosystem: **Tuya Smart** (works with Tuya Smart / Smart Life apps, Alexa, Google Assistant).
- Power monitoring (HLW8012-style energy metering) in the same family.

## Tasmota / firmware situation

- **NVS-SOCKETF-W (old):** ESP8266, Tasmota template exists at
  `templates.blakadder.com/nivian_NVS-SOCKETF-W.html` (GPIO: Relay1=15, Button1=13, Led1i=2,
  HLW8012 CF=5/CF1=14/SELi=12; install via Tuya-Convert). Blakadder warns newer Tuya devices
  ship a WiFi module **incompatible with Tasmota** — probe the chip before promising a reflash.
- **NVS-SOCKETF-W2 (new):** **no Tasmota template** (404 on blakadder). Do NOT assume ESP8266 —
  newer Tuya modules (BK7231N/T2, WB3S, etc.) need OpenBeken or are cloud-locked. For a fast
  actuator, prefer local API control below over reflashing.

## Local control (no cloud) — tinytuya

```bash
python -m pip install tinytuya
python -m tinytuya scan          # 18s UDP broadcast on 6666/6667/7000 -> writes snapshot.json
```

### VERIFIED working control recipe (2026-08-06, protocol discovered)

```python
import tinytuya
d = tinytuya.Device(DEV_ID, IP, LOCAL_KEY, version=3.4)  # <-- 3.4, NOT 3.3!
d.set_socketTimeout(5)
s = d.status()   # -> {'dps': {'1': False, '20': 2272, '22': 564, ...}}
d.set_status(True, 1)   # ON, ack: {'dps': {'1': True}}
d.set_status(False, 1)  # OFF, ack: {'dps': {'1': False}}
```

- **Protocol version = 3.4** (NOT 3.3). 3.1–3.3 → `{'Error': 'Unexpected Payload from Device',
  'Err': '904'}`. Tried 3.1/3.2/3.3/3.4; 3.4 is the only one that works on this plug
  (BK7231N/CB2S — newer Tuya devices moved past 3.3).
- **dps dict keys are STRINGS** (`'1'`, `'20'`, `'22'`, `'23'`). Reading with int keys
  (`dps.get(1)`) returns None silently — looks like the device is mute when it isn't.
  Verified values: `dps['1']`=relay True/False, `dps['20']`=voltage×10 (2272=227.2V),
  `dps['22']`=power×10 (564=56.4W), `dps['21']`=current×10, `dps['23']`=energy Wh×100.
- **Use a FRESH tinytuya.Device instance per request** (re-create before each call). Reusing
  one instance across calls works a couple of times then goes silent (empty/None dps).
- Full round-trip verified: initial `relay='False'` → ON ack `{'1': True}` → read-back
  `relay='True'` → OFF ack `{'1': False}` → read-back `relay='False'`. Status read + command
  ack + read-back all confirmed. Latency ~50–100 ms, no cloud/internet involved.
- Output "New Broadcast from App at <ip>" = a Tuya app (phone) is live on the LAN — means the
  plug is paired to that account (good sign).
- `Found 0 devices` while the app broadcast is present = plug is **in pairing mode / not yet on
  WiFi / asleep** — not a dead end. The plug must first be added in the Tuya Smart app.
- Local control (`tinytuya.OutletDevice(DEVICE_ID, IP, LOCAL_KEY)`, port 6668, AES-encrypted)
  requires **DEVICE_ID + LOCAL_KEY**, which are NOT obtainable from the device itself. Get them:
  1. Tuya IoT Platform (iot.tuya.com): create a Cloud project, link your Tuya Smart app account
     (QR/link step) → API lists devices with `id` + `local_key`. Free tier suffices. Use the
     **Europe region** when the share links use `m-eu.smart321.com` / `app-share-eu`.
     **VERIFIED exact call (2026-08-06):** `tinytuya.Cloud(apiRegion="eu", apiKey=ACCESS_ID,
     apiSecret=ACCESS_SECRET).getdevices(verbose=False)` → list of dicts with
     `id` (=device_id), `key` (=local_key), `mac`, `uuid`, `sn`, `category` ("cz"=plug),
     `product_id`, `model` (contains chip: "CB2S-BK7231N"), `sub: false`. Note the param is
     **apiRegion=**, not region= — wrong kwarg → AttributeError NoneType.lower.
  2. `python -m tinytuya wizard` — scans network, then walks through the IoT-platform account
     link to fetch keys for every device found.
- Caveat: local_key can change if the device is re-paired in the app; re-fetch after re-pairing.

## Discovery on the LAN — validated recipe (2026-08-06)

1. `python -m tinytuya scan` (18 s UDP) found `New Broadcast from App` but **0 devices** even
   though the plug was online — newer Tuya devices ignore UDP broadcast scans. **"Found 0
   devices" is INCONCLUSIVE, not proof of absence.**
2. **Reliable detection = TCP port 6668 open.** Ping-sweep the subnet, then socket-connect each
   live host on 6668 (also check 80/8080). Our plug answered at `192.168.137.109:6668 OPEN`.
3. Alive-check without keys: `tinytuya.Device("0"*20, ip, "0"*16, version=3.1).status()` →
   `{'Error': 'Unexpected Payload from Device', 'Err': '904'}` = **device alive, needs valid
   local_key** (version 3.1 is the right probe for this plug).
4. UDP unicast probes (6666/6667/7000) and raw TCP frames get NO reply without a valid
   key+CRC — expected behavior, not a failure.
5. **device_id WITHOUT cloud via share link** (validated — user had no QR code): in the app,
   copy the device share link `https://m-eu.smart321.com/<code>`; curl with a mobile UA follows
   302 to `https://app-share-eu.ismartlife.me/?deploy=EU&code=...`; the HTML embeds
   `__NEXT_DATA__` JSON → `pageProps.shareState.shareInfo.resId` = **device_id** (e.g.
   `bfd23bfc0bdd93b6904c3s`), plus `resName` ("Smart plug"), `groupId`, `valid: true`.

## Topology note (validated)

The plug was paired to a **Windows hotspot subnet (192.168.137.x) that the PC itself hosts** —
PC and plug share L2, so local tinytuya control works directly. If the plug sits behind a
separate router/AP with its own subnet, tinytuya broadcasts will NOT reach it (or vice versa);
either bridge the networks or run the SuperGuard server on the plug's subnet. Windows `arp -a`
output is cp866 — decode with `iconv -f cp866 -t utf-8` before parsing.

## SuperGuard integration

- Wire the floodlight/siren load through the plug; control = plug ON/OFF.
- Actuator module gains a `tuya` mode: `tinytuya.OutletDevice(device_id, ip, local_key).set_status(True/False, 1)`.
- Do the IoT-platform key fetch ONCE per site at install; store keys in the site config.
- Bonus vs ESP32: plug works standalone from the Tuya app too (manual override, no cloud fee
  for the base local protocol); drawback: needs LAN + local_key provisioning step.
