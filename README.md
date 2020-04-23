# happier
A prototype tool for managing Home Assistant config through the command line.

We are currently in the planning and prototyping stage

## What is it?

A tool for managing Home Assistant configuration via Kubernetes inspired manifest files. These are simple yaml fragments, but we use the Home Assistant API to apply them at runtime. For example, lets pair a integration that is config entries based only, rename some of the entities it adds, set up a scene with one of the entities and then add an automation that triggers the scene:

```bash
happier apply -f - <<EOF
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
EOF
```

This can all be applied at runtime through the existing API that the frontend uses. The changes will show up in the running system without having to bounce HA. The manifest is safe to apply multiple times - it is idempotent.

## What is it for?

### Configuration sharing

Some configuration can now be done in the UI. It's hard to share this with the community because it's baked in to JSON files in .storage, and even if it was safe to share it's still hard to integrate as you are only supposed to edit it via the UI.

### Configuration as YAML

Home Assistant has endless conversations about two seemingly opposite ends of the configuration spectrum:

 * People who want to manage Home Assistant through the UI only, not with text editors.
 * People who want to configure Home Assistant like a traditional Unix daemon. With text editors.

Right now there is a compromise (documented [here](https://github.com/home-assistant/architecture/blob/master/adr/0010-integration-configuration.md)).

This is still not enough for some people who want to treat their configuration as code. It is not a satisfying user experience for them to use Git to manage UI based configuration as they have to version what is effectively an output of a deployment rather than an input to a deployment.

### Backup

It is **not** a replacement for a full backup. It does not contain any runtime state. This includes things like:

 * Tokens or encryptions generated at pairing time that aren't in config
 * Data Home Assistant uses to track entities in different systems - for example, how to associate HomeKit Bridge accessories with Home Assistant entities
  * ...

Howevever if you only ever configure Home Assistant using it, then it maybe a way to turn a blank Home Assistant install into something like the one that you lost.
