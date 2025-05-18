## Connection with a Zoom call without inherent audio devices

This is only important if you want to connect to a Zoom call via an headless unix-based Server.

## Installation 

Installing alsa-utils, if not installed already, should suffice.

```bash
sudo apt-get install alsa-utils
```

## Setup

1. Start an ALSA Loopback Device.

```bash
sudo modprobe snd-aloop
```
You can check if this worked using aplay (you should see Loopback devices).
```bash
aplay -l
```

2. Configure your asound config for the loopback device being default

    1. Either by changing it for your User via editing/creating the /.asoundrc file

    2. Or by changing it system-wide via editing/creating the /etc/asound.conf file
    
```text
pcm.!default {
    type plug
    slave.pcm "loopout"
}

pcm.loopout {
    type hw
    card Loopback
    device 0
    subdevice 0
}

ctl.!default {
    type hw
    card Loopback
}
```