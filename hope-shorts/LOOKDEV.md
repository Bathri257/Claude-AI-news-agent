# Unga Naala Mudiyum — look development (v2)

Frames live in `lookdev/` (2160×3840, 9:16). Nothing is animated yet: this pass agrees on the look first.

## The characters

**Him (35–38).** Lean, mild brown skin, light stubble and a moustache. Matte-black half helmet with a thin blue
stripe and a chin strap. Sky-blue shirt with a fine woven texture and the sleeves rolled to the elbow. It is damp in
darker patches across the shoulders and upper back, where the drizzle soaks through first. Grey trousers, brown
belt with a brass buckle, brown leather shoes. A small stitched scar on the forearm. After the fall he has mud on
the knee.

**The kid (7–8).** Warm brown skin, a big smile that squints his eyes. A yellow raincoat with the hood up and beads
of rain on the hood, worn over a white school uniform (the collar shows at the neck). White socks, black school
shoes. A green school bag in a fitted green rain cover with elastic edges and droplets. **The same stitched scar,
in the same place on the forearm.** Yellow is my choice for the raincoat: in a grey street it is the only warm
colour, so your eye finds him in every wide shot. It is easy to change.

**The bike.** A dark-blue dual-purpose commuter: white tank with a blue sweep, black flat seat, high front
fender, fork gaiters, spoked wheels with knobby tyres, upswept silencer, red rear spring. It is modelled on the
proportions of that class of bike but has no badges or logos.

**Scale (real-world).** Man 1.72 m, kid 1.28 m, bike 2.1 m long and 1.1 m to the handlebar. Every shot is placed
through a camera model in metres, so a hatchback reaches about his chest, a city bus stands well above him, and
anything further away sits higher in the frame.

## The backdrop — OMR, near the big glass towers, Monday 8:40 AM

- **Sky.** Low, flat monsoon overcast in a cool grey-blue, darker at the top. There's no sun and no shadow direction, just
  soft light from everywhere.
- **Skyline.** Tall blue-grey glass towers dominate the distance, with a visible floor grid, a few office lights
  already on, and a diagonal sky reflection on the glass. Haze from the drizzle softens them. In front sit long,
  low IT-park blocks with horizontal bands of glass. The towers are generic and carry no signage.
- **Roadside.** A grey compound wall, rain trees with dense dark canopies (lighter on top, nearly black
  underneath), tall double-arm street lights, a paver footpath, and the **black-and-yellow painted kerb** you see
  all along Chennai's arterial roads. People wait under black and maroon umbrellas.
- **The road.** Two lanes in our direction with a dashed white divider. The asphalt is dark and wet with a soft sheen.
  Headlights are on even in daylight, and they and the tail lights smear into long vertical streaks on the wet
  road. There are **clear puddles** everywhere: small ones with rain rings, and one large foreground puddle that mirrors
  the towers upside down.
- **Traffic.** A green-and-cream city bus, sedans and hatchbacks, autos, and scooter riders in raincoats. In
  every shot after the fall the traffic is motion-blurred streaks: the city never stops moving.
- **Rain.** A fine, slanting drizzle. It's not a downpour, just enough to sting a rider's face and fog a visor. Close drops
  are blurred streaks in front of the lens. Wheels throw a fine spray.
- **Grade.** Cool and desaturated, with a soft vignette and fine film grain. The only warm notes are the yellow
  raincoat, the kerb, the headlights and his skin.

## The flashback (borrowing the *principle* of the Ratatouille moment, not its look)

The critic's memory in Ratatouille works because one small sensation **yanks him out of the present** into a
warm, glowing, child-height memory, and then drops him back changed. We use the same grammar:

1. **Trigger:** in close-up, the two matching scars side by side.
2. **The push-in:** the camera rushes into his eyes. Rain sound drops out to silence, then one soft note.
3. **The memory:** a sunlit 90s small-town lane with tiled-roof houses, coconut palms and a temple tower in the
   haze. The young him, in a white uniform with the same green bag and the same scar, helps an old man lift a
   fallen black bicycle. That rhymes exactly with what the kid is doing for him now. The camera sits at a child's
   height. The colours are golden and amber, with bloom, light shafts, floating dust and soft, glowing edges.
4. **The return:** a hard cut back to the cold, grey rain, and his face has changed.

## Running this on your laptop (Windows, Acer Nitro 5)

1. Install **Node.js 20 or newer** from nodejs.org.
2. Get the project from the `claude/fervent-ride-65aecz` branch, then in a terminal:
   ```
   cd hope-shorts
   npm install
   ```
3. Preview interactively: `npm run studio` (opens in your browser; click any frame to inspect it).
4. Re-render these stills in high resolution (Git Bash or WSL; about a minute):
   ```
   SCALE=2 ./render-stills.sh
   ```
   In plain PowerShell, render one at a time instead:
   `npx remotion still src/index.ts Cut1 out/look/Cut1.png --scale=2`
5. Once the animation is built, the overnight render will be a single command (it will be added here), using
   `--concurrency=2` so 8 GB of RAM is enough.
