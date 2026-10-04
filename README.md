# Prehnite Volley

Full-colour Python 3 neon vertical volley arcade for [ElbowOS](https://x.com/ElbowOS).

You hold the bottom prehnite paddle. The amber rival holds the top. Return the shard, clip floating gems, and chain the combo. Side rails flash coral on a wall hit. Passing the rival scores a smash.

This is an original volley. It is not a commercial game, not a ROM, and not an emulator.

## Play

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 prehnite_volley.py --play
```

A / D or arrow keys move the paddle. R restarts.

## Record a 9:16 reel

```bash
python3 prehnite_volley.py --record
```

Headless path uses `SDL_VIDEODRIVER=dummy`, draws 1080x1920 at 30fps for 15 seconds, and pipes RGB frames to ffmpeg (`libx264`, `yuv420p`, CRF 20, `+faststart`).

## Links

- Featured account: https://x.com/ElbowOS
- Drive reel: https://drive.google.com/file/d/1LU5m2z9agmJP0kzx50FbxGeKU8DZPK4s/view?usp=drivesdk
- Posted copy: https://drive.google.com/file/d/16YfZE8IR8DKExgAP_VaH_Ia-ft_9eP2y/view?usp=drivesdk
