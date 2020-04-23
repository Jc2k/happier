# happier
A prototype tool for managing Home Assistant config through the command line.

We are currently in the planning and prototyping stage. Subscribe to [#9](https://github.com/Jc2k/happier/issues/9) for sporadic updates.

## What is it?

A tool for managing Home Assistant configuration via Kubernetes inspired manifest files. These are simple yaml fragments, but we use the Home Assistant API to apply them at runtime. For example, lets pair a integration that is config entries based only, rename some of the entities it adds, set up a scene with one of the entities and then add an automation that triggers the scene. You can have a manifest that looks like this:

```yaml
kind: Integration
selector:
  domain: homekit_controller
  address: 1.2.3.4
  device:
    serial: 1234567

config:
  pincode: 123-45-789

options:
  setting1: foo
  setting2: bar
---
kind: Entity
selector:
  device:
    serial: 1234567
  class: temperature
name: My Homekit Temperature Sensor
entity_id: sensor.living_room_remperature
area: Living Room
---
kind: Entity
selector:
  device:
    serial: 234567
  class: lightbulb
name: My Homekit Light Bulb
entity_id: light.living_room
area: Living Room
---
kind: Scene
name: Hot
entities:
  light.living_room:
    state: on
    xy_color: [0.33, 0.66]
    brightness: 200
---
kind: Automation
name: LivingRoomTempHot
description: It's very warm in the living room
trigger:
  - type: temperature
    above: 25
    entity_id: sensor.bunnywood_temperature
action:
  - scene: Hot
```

and run it with:

```bash
happier apply manifest.yaml
```

This can all be applied at runtime through the existing API that the frontend uses. The changes will show up in the running system without having to bounce HA. The manifest is safe to apply multiple times - it is idempotent.


## What is it for?

### Configuration as YAML

Treat your config as code. Check it into Git. Generate it from other systems. Apply it as part of a CI build and deploy pipeline.

### Configuration sharing

Some configuration can now be done in the UI. It's hard to share this with the community because it's baked in to JSON files in .storage, and even if it was safe to share it's still hard to integrate as you are only supposed to edit it via the UI.

### Backup

It is **not** a replacement for a full backup. It does not contain any runtime state. This includes things like:

 * Tokens or encryptions generated at pairing time that aren't in config
 * Data Home Assistant uses to track entities in different systems - for example, how to associate HomeKit Bridge accessories with Home Assistant entities
  * ...

Howevever if you only ever configure Home Assistant using it, then it maybe a way to turn a blank Home Assistant install into something like the one that you lost.

### Debugging

In terms of reproducing a users problem, having a manifest might give clues into the state of their system.

## Installation

We are not even to the alpha stage yet so there isn't really anything to install unless you are a developer planning to contribute.

## Non-Functional Requirements

### Declarative not imperative

We are describing a target state, not a change we want to make. Exactly like an ordinary config file. This approach needs to be idempotent. This raises the bar for the code we need to write but makes it much safer for the end user. It unlocks stricter validation and more realistic dry runs.

### Immediate visibility of changes

We go through the API and apply changes to a running system. Changes are visible as quickly as they would be if made via the UI.

### Secure
We use the Home Assistant API, which is protected by access keys. We do not need access to the file system where the Home Assistant config lives. We do not need to run as a particular unix user. We can run from anywhere we can access the Home Assistant API (i.e. UI).

### Safety

We go through the API, so we can't apply config that the UI wouldn't allow. A bug in happier can only corrupt Home Assistant if the Home Assistant API also allows that bug. We aren't directly modifying files on disk, so we can't directly cause data or config loss.
 
## Concepts

### Selectors

Sometimes we can't predict what identifier a device or entity will be given, but to be safe and idempotent we still need to be able to find the one that already exists. So we need selectors. We may need to combine multiple selectors to find a single object.

* `address`: Used when adding config entries - filter discoveries by IP address.
* `domain`: restricts a search by the domain of an integration - for example `hue`
* `device`: restricts a search using the device registry. For example, a device has a serial number and that is a fairly stable identifier.
* `class`: this can be combined with `device` to find a particular entity within a device.
 
## Q+A
 
### How do I deal with secrets?
 
This is a very opinionated area, so we've tried to leave it to end users. The general approach is to use templates to seperate different parts of your config. Dozens of config management tools provide way to templatize yaml, and rather than make a bad one and bake it it we suggest you chain tools. It's the unix way!
 
* [ytt](https://get-ytt.io/)
* [j2cli](https://github.com/kolypto/j2cli)
* [gomplate](https://github.com/hairyhenderson/gomplate)

## Contributing
 
All contributions must be under the same licence and terms as contribution to a Home Assistant component. They must also meet similiar code quality checks.
 
We target the same platforms and python versions as Home Assistant Core.

You can build a dev environment with:
 
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
 
You need to make a config file with the connection details for your HA instance:
 
```bash
cat > ~/.config/happier/config.yaml <<EOF
default:
  host: ha.yourhost.co.uk
  port: 443
  access_token: 1234.abcd.abcedf-fffff_wwe
EOF
```

I've only tested with TLS turned on with a real certificate, so running without TLS probably won't work.

You need a manifest to apply. At the moment only Area and Dashboard are working:

```yaml
kind: Area
version: v1alpha1
name: Living Room Test
---
kind: Dashboard
version: v1alpha1
url_path: my-batteries
title: My Batteries
views:
- title: System Status
  cards:
  - title: Battery Status
    type: entities
    path: status
    entities:
    - entity: sensor.battery_1
    - entity: sensor.battery_2
    - entity: sensor.battery_3
    - entity: sensor.battery_4
    - entity: sensor.battery_5
    - entity: sensor.battery_6
```

You can run with:

```bash
python -m happier apply mainfest.yaml
```
