# Unga Naala Mudiyum (ep001): AI video prompt sheet

**Logline:** A lean man falls off his heavy bike on a rainy OMR morning; the whole city watches and moves on, until a small boy with the same scar helps him lift it.

**Takeaway:** Today, stop for someone the city walks past.

18 shots, 77 s of raw footage, edited down to about 65 s. Aspect ratio 9:16.

## How to use this sheet

1. **Make the references once (Step 1).** Generate each reference image, regenerate until you love it, and save the best one. Reuse these files for every shot. They are your cast and set.
2. **Make a start frame for each shot (Step 2a).** Use a text-to-image model and attach the listed reference images ("reference" / "character" / "elements" input). Iterate here: images are far cheaper than video.
3. **Animate only approved frames (Step 2b).** Use image-to-video with the start frame plus the motion prompt, and generate 5 s clips (10 s only where noted). Paste the negative prompt where the tool has one.
4. **Leave text, voice and music out of the generation.** Captions, the kid's line and the music are added in the edit, so they stay sharp and consistent.
5. **Name clips by shot id** (`S01.mp4`, `S02.mp4`, ...) in `clips/`, so the assembly step can find them.

**Trial run (proof of concept):** generate only the key shots first: S03, S05, S07, S10, S11, S12, S14, S17. If those eight look right together, generate the rest.

**Negative prompt (all shots):**
```
text, captions, subtitles, watermark, logo, brand names, extra fingers, deformed hands, distorted face, face morphing, identity drift, flicker, warped wheels, duplicate limbs, horizontal frame
```

## Step 1: reference images (generate once, reuse for every shot)

### REF_HERO · aspect 16:9
```
Character reference sheet on a plain light-grey background. A lean South Indian man in his late 30s with mild brown skin, short black hair, light stubble and a neat moustache, wearing a matte-black open-face half helmet with a thin blue stripe, a sky-blue textured cotton shirt with the sleeves rolled to the elbow and damp darker patches on the shoulders, grey trousers, a brown leather belt and brown leather shoes, with a small stitched scar on his left forearm. Three full-body views side by side (front, three-quarter, side profile) in a neutral standing pose, plus a close-up of the face and a close-up of the forearm scar. Consistent proportions, 1.72 m tall adult. Stylized 3D animated feature-film look: soft, rounded, appealing character design with expressive eyes, gentle subsurface skin shading, painterly cinematic lighting, shallow depth of field, subtle film grain.
```

### REF_KID · aspect 16:9
```
Character reference sheet on a plain light-grey background. A 7-year-old South Indian boy with warm brown skin, big bright eyes and a warm smile, wearing a bright yellow raincoat with the hood up and raindrops beading on the hood, a white school-uniform collar showing at the neck, white shorts, white socks and black school shoes, carrying a green school backpack in a fitted green rain cover, with a small stitched scar on his left forearm. Three full-body views side by side (front, three-quarter, side profile) in a neutral standing pose, plus a close-up of the smiling face with raindrops on the hood and a close-up of the forearm scar. 1.28 m tall child. Stylized 3D animated feature-film look: soft, rounded, appealing character design with expressive eyes, gentle subsurface skin shading, painterly cinematic lighting, shallow depth of field, subtle film grain.
```

### REF_BIKE · aspect 16:9
```
Product-style reference sheet on a plain light-grey background. A dark-blue dual-purpose 150cc motorcycle with a white fuel tank, a black flat seat, a high front fender, fork gaiters, spoked wheels and knobby tyres, no logos or badges. Side view, three-quarter front view and three-quarter rear view. Stylized 3D animated feature-film look: soft, rounded, appealing character design with expressive eyes, gentle subsurface skin shading, painterly cinematic lighting, shallow depth of field, subtle film grain.
```

### REF_LOCATION · aspect 9:16
```
Environment concept art, no people in the foreground: the OMR IT corridor in Chennai, India: a busy two-lane road beside tall blue-grey glass office towers, rain trees, a black-and-yellow painted kerb, a paver footpath, wet dark asphalt with clear puddles, steady fine monsoon drizzle, overcast Monday morning, vehicles with headlights on. Wide street-level view showing both lanes, the kerb, the footpath with a bus stop, and the glass towers rising into the haze. Stylized 3D animated feature-film look: soft, rounded, appealing character design with expressive eyes, gentle subsurface skin shading, painterly cinematic lighting, shallow depth of field, subtle film grain. Muted teal-grey monsoon palette; the only warm accents are the yellow raincoat, headlights and skin tones.
```

## Step 2: shots

### S01 · 5 s · drone descend + push in

*Establish the place, the weather and the busy indifference of the city.*  
Timeline 0–5 s · attach: REF_LOCATION

**2a · Start frame (text-to-image, 9:16):**
```
Slow aerial drone view looking down on the OMR IT corridor in Chennai, India: a busy two-lane road beside tall blue-grey glass office towers, rain trees, a black-and-yellow painted kerb, a paver footpath, wet dark asphalt with clear puddles, steady fine monsoon drizzle, overcast Monday morning, vehicles with headlights on. Traffic crawls in both lanes: a green-and-cream city bus, autorickshaws, scooters with riders in raincoats. Umbrellas on the footpath; puddles reflect the grey sky and the towers. Stylized 3D animated feature-film look: soft, rounded, appealing character design with expressive eyes, gentle subsurface skin shading, painterly cinematic lighting, shallow depth of field, subtle film grain. Muted teal-grey monsoon palette; the only warm accents are the yellow raincoat, headlights and skin tones.
```
**2b · Motion (image-to-video):**
```
The camera slowly descends and pushes forward toward the road. Rain falls diagonally, traffic moves steadily, puddles ripple.
```
**Caption in edit:** OMR · MONDAY · 8:40 AM  
**Sound:** steady rain, distant traffic hiss, horns

### S02 · 4 s · static, slight handheld

*Plant the kid early, so his return feels earned, not convenient.*  
Timeline 5–9 s · attach: REF_KID, REF_LOCATION

**2a · Start frame (text-to-image, 9:16):**
```
Street-level medium shot of a small boy standing at the kerb waiting to cross, holding his bag straps, raindrops beading on his hood, looking left at the traffic. Blurred vehicles pass in the foreground; the road and glass towers are softly out of focus behind him. The boy: A 7-year-old South Indian boy with warm brown skin, big bright eyes and a warm smile, wearing a bright yellow raincoat with the hood up and raindrops beading on the hood, a white school-uniform collar showing at the neck, white shorts, white socks and black school shoes, carrying a green school backpack in a fitted green rain cover, with a small stitched scar on his left forearm. Setting: the OMR IT corridor in Chennai, India: a busy two-lane road beside tall blue-grey glass office towers, rain trees, a black-and-yellow painted kerb, a paver footpath, wet dark asphalt with clear puddles, steady fine monsoon drizzle, overcast Monday morning, vehicles with headlights on. Stylized 3D animated feature-film look: soft, rounded, appealing character design with expressive eyes, gentle subsurface skin shading, painterly cinematic lighting, shallow depth of field, subtle film grain. Muted teal-grey monsoon palette; the only warm accents are the yellow raincoat, headlights and skin tones.
```
**2b · Motion (image-to-video):**
```
The boy blinks and shifts his weight, watching the cars. Rain drips from the edge of his hood. Foreground traffic streaks past. Slight handheld drift.
```
**Sound:** rain on raincoat, passing cars

### S03 · 5 s · side tracking ★ key shot

*Meet him: tired, a little out of his depth, carrying a bike too heavy for him.*  
Timeline 9–14 s · attach: REF_HERO, REF_BIKE

**2a · Start frame (text-to-image, 9:16):**
```
Side tracking shot at wheel height of a lean man riding a motorcycle in the left lane, squinting against the drizzle, shoulders tense; the bike looks slightly too big and heavy for his lean frame. Motion-blurred traffic and glass towers behind. The man: A lean South Indian man in his late 30s with mild brown skin, short black hair, light stubble and a neat moustache, wearing a matte-black open-face half helmet with a thin blue stripe, a sky-blue textured cotton shirt with the sleeves rolled to the elbow and damp darker patches on the shoulders, grey trousers, a brown leather belt and brown leather shoes, with a small stitched scar on his left forearm. The motorcycle: A dark-blue dual-purpose 150cc motorcycle with a white fuel tank, a black flat seat, a high front fender, fork gaiters, spoked wheels and knobby tyres, no logos or badges. Stylized 3D animated feature-film look: soft, rounded, appealing character design with expressive eyes, gentle subsurface skin shading, painterly cinematic lighting, shallow depth of field, subtle film grain. Muted teal-grey monsoon palette; the only warm accents are the yellow raincoat, headlights and skin tones.
```
**2b · Motion (image-to-video):**
```
The camera tracks alongside at his speed. The background streaks past. Rain hits his face; the front wheel throws a fine spray. He quickly wipes water from his eyes with one hand, then grips the handlebar again.
```
**Caption in edit:** His bike was always a little too heavy for him.  
**Sound:** engine idle hum, tyres on wet road

### S04 · 3 s · low static, jolt

*The hidden pothole. Show the cause, not the crash.*  
Timeline 14–17 s · attach: REF_BIKE

**2a · Start frame (text-to-image, 9:16):**
```
Low-angle close-up of the spoked front wheel of a dark-blue motorcycle rolling toward a deep rain-filled pothole hidden inside a puddle on wet asphalt; raindrops hit the puddle. Stylized 3D animated feature-film look: soft, rounded, appealing character design with expressive eyes, gentle subsurface skin shading, painterly cinematic lighting, shallow depth of field, subtle film grain. Muted teal-grey monsoon palette; the only warm accents are the yellow raincoat, headlights and skin tones.
```
**2b · Motion (image-to-video):**
```
The wheel rolls forward and drops into the pothole. A burst of muddy water splashes toward the camera and the frame jolts. Cut on impact.
```
**Sound:** thud, splash, then sudden silence

### S05 · 4 s · static wide ★ key shot

*Aftermath. Nobody slows down.*  
Timeline 17–21 s · attach: REF_HERO, REF_BIKE, REF_LOCATION

**2a · Start frame (text-to-image, 9:16):**
```
Wide shot from the footpath: a motorcycle lying on its side in the road, its front wheel still slowly spinning; the rider sits on the wet asphalt beside it, pushing himself up on one arm. Traffic passes around him without stopping. The man: A lean South Indian man in his late 30s with mild brown skin, short black hair, light stubble and a neat moustache, wearing a matte-black open-face half helmet with a thin blue stripe, a sky-blue textured cotton shirt with the sleeves rolled to the elbow and damp darker patches on the shoulders, grey trousers, a brown leather belt and brown leather shoes, with a small stitched scar on his left forearm. The motorcycle: A dark-blue dual-purpose 150cc motorcycle with a white fuel tank, a black flat seat, a high front fender, fork gaiters, spoked wheels and knobby tyres, no logos or badges. Setting: the OMR IT corridor in Chennai, India: a busy two-lane road beside tall blue-grey glass office towers, rain trees, a black-and-yellow painted kerb, a paver footpath, wet dark asphalt with clear puddles, steady fine monsoon drizzle, overcast Monday morning, vehicles with headlights on. Stylized 3D animated feature-film look: soft, rounded, appealing character design with expressive eyes, gentle subsurface skin shading, painterly cinematic lighting, shallow depth of field, subtle film grain. Muted teal-grey monsoon palette; the only warm accents are the yellow raincoat, headlights and skin tones.
```
**2b · Motion (image-to-video):**
```
He pushes himself up to sitting and shakes rain off his hand. Cars and an autorickshaw pass behind him without slowing. The front wheel slows to a stop.
```
**Sound:** rain returns, traffic keeps passing

### S06 · 5 s · static medium

*He isn't hurt; his pride is.*  
Timeline 21–26 s · attach: REF_HERO

**2a · Start frame (text-to-image, 9:16):**
```
Medium shot of a man standing in the road, mud on the knee of his grey trousers, shirt damp, brushing dirt off his trousers, more embarrassed than hurt. Busy rainy road out of focus behind him. The man: A lean South Indian man in his late 30s with mild brown skin, short black hair, light stubble and a neat moustache, wearing a matte-black open-face half helmet with a thin blue stripe, a sky-blue textured cotton shirt with the sleeves rolled to the elbow and damp darker patches on the shoulders, grey trousers, a brown leather belt and brown leather shoes, with a small stitched scar on his left forearm. Stylized 3D animated feature-film look: soft, rounded, appealing character design with expressive eyes, gentle subsurface skin shading, painterly cinematic lighting, shallow depth of field, subtle film grain. Muted teal-grey monsoon palette; the only warm accents are the yellow raincoat, headlights and skin tones.
```
**2b · Motion (image-to-video):**
```
He brushes his trousers twice and straightens up, then slowly lifts his head and looks around.
```
**Caption in edit:** He wasn't hurt.  
**Sound:** rain, his breathing

### S07 · 5 s · POV, slow motion ★ key shot

*The stare: everyone sees, no one stops.*  
Timeline 26–31 s · attach: REF_LOCATION

**2a · Start frame (text-to-image, 9:16):**
```
Point of view across a rainy road: people under black umbrellas at a bus stop on the footpath, all looking straight at the camera. A woman in a magenta kurta, an office worker in a white shirt, a security guard. Traffic blurs between us and them. Setting: the OMR IT corridor in Chennai, India: a busy two-lane road beside tall blue-grey glass office towers, rain trees, a black-and-yellow painted kerb, a paver footpath, wet dark asphalt with clear puddles, steady fine monsoon drizzle, overcast Monday morning, vehicles with headlights on. Stylized 3D animated feature-film look: soft, rounded, appealing character design with expressive eyes, gentle subsurface skin shading, painterly cinematic lighting, shallow depth of field, subtle film grain. Muted teal-grey monsoon palette; the only warm accents are the yellow raincoat, headlights and skin tones.
```
**2b · Motion (image-to-video):**
```
Slow motion. They stare for a moment, then one by one look away and back to their phones. Traffic streaks past in the foreground.
```
**Caption in edit:** But the whole city saw… and kept moving.  
**Sound:** muffled, slowed traffic; rain fades low

### S08 · 4 s · static

*First attempt.*  
Timeline 31–35 s · attach: REF_HERO, REF_BIKE

**2a · Start frame (text-to-image, 9:16):**
```
Medium three-quarter shot of a man bending over a motorcycle that lies on the wet road, both hands on the handlebar, about to lift it. The man: A lean South Indian man in his late 30s with mild brown skin, short black hair, light stubble and a neat moustache, wearing a matte-black open-face half helmet with a thin blue stripe, a sky-blue textured cotton shirt with the sleeves rolled to the elbow and damp darker patches on the shoulders, grey trousers, a brown leather belt and brown leather shoes, with a small stitched scar on his left forearm. The motorcycle: A dark-blue dual-purpose 150cc motorcycle with a white fuel tank, a black flat seat, a high front fender, fork gaiters, spoked wheels and knobby tyres, no logos or badges. Stylized 3D animated feature-film look: soft, rounded, appealing character design with expressive eyes, gentle subsurface skin shading, painterly cinematic lighting, shallow depth of field, subtle film grain. Muted teal-grey monsoon palette; the only warm accents are the yellow raincoat, headlights and skin tones.
```
**2b · Motion (image-to-video):**
```
He pulls hard. The bike rises a little, then slides back down onto the road. He exhales.
```
**Caption in edit:** Once.  
**Sound:** metal scrape, exhale

### S09 · 4 s · low close-up

*Second attempt. The low point.*  
Timeline 35–39 s · attach: REF_HERO, REF_BIKE

**2a · Start frame (text-to-image, 9:16):**
```
Low close shot of a man's face, straining, rain running down from under his half helmet, teeth clenched; the white tank of a motorcycle in the foreground. The man: A lean South Indian man in his late 30s with mild brown skin, short black hair, light stubble and a neat moustache, wearing a matte-black open-face half helmet with a thin blue stripe, a sky-blue textured cotton shirt with the sleeves rolled to the elbow and damp darker patches on the shoulders, grey trousers, a brown leather belt and brown leather shoes, with a small stitched scar on his left forearm. Stylized 3D animated feature-film look: soft, rounded, appealing character design with expressive eyes, gentle subsurface skin shading, painterly cinematic lighting, shallow depth of field, subtle film grain. Muted teal-grey monsoon palette; the only warm accents are the yellow raincoat, headlights and skin tones.
```
**2b · Motion (image-to-video):**
```
He strains; the bike lifts halfway and his arms shake; it drops again. He closes his eyes for a second.
```
**Caption in edit:** Twice.  
**Sound:** strain, bike drops, rain louder

### S10 · 5 s · macro, slow push in ★ key shot

*The third try: a small hand with the same scar.*  
Timeline 39–44 s · attach: REF_HERO, REF_KID

**2a · Start frame (text-to-image, 9:16):**
```
Extreme close-up: an adult man's brown hand grips the black seat of a fallen motorcycle, a small stitched scar on his forearm below a rolled sky-blue sleeve. From the left, a small child's hand in a yellow raincoat sleeve presses flat against the seat beside his, with an identical small stitched scar on the same place on the forearm. Rain beads on both arms. Stylized 3D animated feature-film look: soft, rounded, appealing character design with expressive eyes, gentle subsurface skin shading, painterly cinematic lighting, shallow depth of field, subtle film grain. Muted teal-grey monsoon palette; the only warm accents are the yellow raincoat, headlights and skin tones.
```
**2b · Motion (image-to-video):**
```
Both hands push together and the seat starts to rise. Raindrops tremble on the skin. A very slow push-in on the two scars.
```
**Sound:** music enters: single soft piano note

### S11 · 4 s · static close-up ★ key shot

*The line.*  
Timeline 44–48 s · attach: REF_KID

**2a · Start frame (text-to-image, 9:16):**
```
Close-up of a small boy pushing a motorcycle with both hands, looking up at the man with a warm, determined smile, his hood dripping. Rainy road softly blurred behind. The boy: A 7-year-old South Indian boy with warm brown skin, big bright eyes and a warm smile, wearing a bright yellow raincoat with the hood up and raindrops beading on the hood, a white school-uniform collar showing at the neck, white shorts, white socks and black school shoes, carrying a green school backpack in a fitted green rain cover, with a small stitched scar on his left forearm. Stylized 3D animated feature-film look: soft, rounded, appealing character design with expressive eyes, gentle subsurface skin shading, painterly cinematic lighting, shallow depth of field, subtle film grain. Muted teal-grey monsoon palette; the only warm accents are the yellow raincoat, headlights and skin tones.
```
**2b · Motion (image-to-video):**
```
He looks up, smiles wide and speaks encouragingly, with a small nod. Raindrops fall from the edge of his hood.
```
**Caption in edit:** “Come on anna, unga naala mudiyum!”  (Come on, brother. You can do it.)  
**Voice in edit:** Child voice, Tamil, bright and sure: "Come on anna, unga naala mudiyum!"  
**Sound:** music builds gently

### S12 · 5 s · static wide, slight push in ★ key shot

*Together, it comes up. The weather turns with him.*  
Timeline 48–53 s · attach: REF_HERO, REF_KID, REF_BIKE, REF_LOCATION

**2a · Start frame (text-to-image, 9:16):**
```
Wide shot: a man and a small boy lift a motorcycle upright together in the road. The drizzle is easing and a break in the clouds lets warm light fall across the wet road. The man: A lean South Indian man in his late 30s with mild brown skin, short black hair, light stubble and a neat moustache, wearing a matte-black open-face half helmet with a thin blue stripe, a sky-blue textured cotton shirt with the sleeves rolled to the elbow and damp darker patches on the shoulders, grey trousers, a brown leather belt and brown leather shoes, with a small stitched scar on his left forearm. The boy: A 7-year-old South Indian boy with warm brown skin, big bright eyes and a warm smile, wearing a bright yellow raincoat with the hood up and raindrops beading on the hood, a white school-uniform collar showing at the neck, white shorts, white socks and black school shoes, carrying a green school backpack in a fitted green rain cover, with a small stitched scar on his left forearm. The motorcycle: A dark-blue dual-purpose 150cc motorcycle with a white fuel tank, a black flat seat, a high front fender, fork gaiters, spoked wheels and knobby tyres, no logos or badges. Setting: the OMR IT corridor in Chennai, India: a busy two-lane road beside tall blue-grey glass office towers, rain trees, a black-and-yellow painted kerb, a paver footpath, wet dark asphalt with clear puddles, steady fine monsoon drizzle, overcast Monday morning, vehicles with headlights on. Stylized 3D animated feature-film look: soft, rounded, appealing character design with expressive eyes, gentle subsurface skin shading, painterly cinematic lighting, shallow depth of field, subtle film grain. Muted teal-grey monsoon palette; the only warm accents are the yellow raincoat, headlights and skin tones.
```
**2b · Motion (image-to-video):**
```
The bike comes fully upright and the man steadies it on its stand. The rain thins; warm light spreads across the puddles.
```
**Caption in edit:** It was just a kid. Maybe eight years old.  
**Sound:** music swells softly, rain thins

### S13 · 3 s · extreme close-up, push in

*The trigger into memory (the Ratatouille move).*  
Timeline 53–56 s · attach: REF_HERO

**2a · Start frame (text-to-image, 9:16):**
```
Extreme close-up of a man's eyes under the brim of a black half helmet, rain on his eyelashes, looking down; a tiny yellow reflection of a raincoat in his pupils. The man: A lean South Indian man in his late 30s with mild brown skin, short black hair, light stubble and a neat moustache, wearing a matte-black open-face half helmet with a thin blue stripe, a sky-blue textured cotton shirt with the sleeves rolled to the elbow and damp darker patches on the shoulders, grey trousers, a brown leather belt and brown leather shoes, with a small stitched scar on his left forearm. Stylized 3D animated feature-film look: soft, rounded, appealing character design with expressive eyes, gentle subsurface skin shading, painterly cinematic lighting, shallow depth of field, subtle film grain. Muted teal-grey monsoon palette; the only warm accents are the yellow raincoat, headlights and skin tones.
```
**2b · Motion (image-to-video):**
```
A very slow push into his eyes. A soft warm light flickers in his pupils.
```
**Sound:** all sound drops out to near-silence

### S14 · 6 s · child-eye-level, gentle drift ★ key shot

*The memory: he used to be this kid.*  
Timeline 56–62 s · attach: REF_KID

**2a · Start frame (text-to-image, 9:16):**
```
A sunny 1990s small-town street in Tamil Nadu with tiled-roof houses, coconut palms and a temple tower in the haze. A young boy helps an old man lift his fallen black bicycle; oranges are spilled on the dusty road; both are smiling. The boy: The same boy as the kid reference, but on a sunny day in the 1990s: white school shirt and shorts, no raincoat, bare head with short black hair, a green school bag without a cover, the same small stitched scar on his left forearm. The old man: An elderly South Indian man in a white shirt and white veshti, grey hair, thick round glasses and a kind, tired face. Warm golden-hour memory: honey and amber tones, soft bloom and halation, sunbeams with floating dust, slightly hazy dreamy edges, camera at a child's eye level. Stylized 3D animated feature-film look: soft, rounded, appealing character design with expressive eyes, gentle subsurface skin shading, painterly cinematic lighting, shallow depth of field, subtle film grain.
```
**2b · Motion (image-to-video):**
```
The boy and the old man raise the bicycle together; the old man pats the boy's head. Dust floats in the sunbeams. Gentle slow motion.
```
**Caption in edit:** He remembered a boy who used to stop for strangers.  
**Sound:** warm room tone, birds, distant temple bell

### S15 · 3 s · static close-up

*Back to now, changed.*  
Timeline 62–65 s · attach: REF_HERO

**2a · Start frame (text-to-image, 9:16):**
```
Close-up of a man's face back in the light rain, softened, eyes wet, the start of a small smile. The man: A lean South Indian man in his late 30s with mild brown skin, short black hair, light stubble and a neat moustache, wearing a matte-black open-face half helmet with a thin blue stripe, a sky-blue textured cotton shirt with the sleeves rolled to the elbow and damp darker patches on the shoulders, grey trousers, a brown leather belt and brown leather shoes, with a small stitched scar on his left forearm. Stylized 3D animated feature-film look: soft, rounded, appealing character design with expressive eyes, gentle subsurface skin shading, painterly cinematic lighting, shallow depth of field, subtle film grain. Muted teal-grey monsoon palette; the only warm accents are the yellow raincoat, headlights and skin tones.
```
**2b · Motion (image-to-video):**
```
He breathes out and smiles slowly. The rain continues gently.
```
**Sound:** hard cut back to rain, softer

### S16 · 4 s · static wide

*The kid finally crosses, because the traffic stops for him.*  
Timeline 65–69 s · attach: REF_HERO, REF_KID, REF_LOCATION

**2a · Start frame (text-to-image, 9:16):**
```
Wide shot: a small boy waves goodbye as he crosses at a zebra crossing; the traffic has stopped for him; a man stands beside his upright motorcycle, watching. The boy: A 7-year-old South Indian boy with warm brown skin, big bright eyes and a warm smile, wearing a bright yellow raincoat with the hood up and raindrops beading on the hood, a white school-uniform collar showing at the neck, white shorts, white socks and black school shoes, carrying a green school backpack in a fitted green rain cover, with a small stitched scar on his left forearm. The man: A lean South Indian man in his late 30s with mild brown skin, short black hair, light stubble and a neat moustache, wearing a matte-black open-face half helmet with a thin blue stripe, a sky-blue textured cotton shirt with the sleeves rolled to the elbow and damp darker patches on the shoulders, grey trousers, a brown leather belt and brown leather shoes, with a small stitched scar on his left forearm. Setting: the OMR IT corridor in Chennai, India: a busy two-lane road beside tall blue-grey glass office towers, rain trees, a black-and-yellow painted kerb, a paver footpath, wet dark asphalt with clear puddles, steady fine monsoon drizzle, overcast Monday morning, vehicles with headlights on. Stylized 3D animated feature-film look: soft, rounded, appealing character design with expressive eyes, gentle subsurface skin shading, painterly cinematic lighting, shallow depth of field, subtle film grain. Muted teal-grey monsoon palette; the only warm accents are the yellow raincoat, headlights and skin tones.
```
**2b · Motion (image-to-video):**
```
The boy waves over his shoulder and skips across. The man raises his hand and waves back.
```
**Sound:** music continues

### S17 · 4 s · slow tracking ★ key shot

*The ripple: he passes it on.*  
Timeline 69–73 s · attach: REF_HERO

**2a · Start frame (text-to-image, 9:16):**
```
Later that day, in golden late-afternoon light after the rain: a man in a damp sky-blue shirt holds his umbrella over an elderly woman as she slowly crosses a busy road; the wet road glows. The man: A lean South Indian man in his late 30s with mild brown skin, short black hair, light stubble and a neat moustache, wearing a matte-black open-face half helmet with a thin blue stripe, a sky-blue textured cotton shirt with the sleeves rolled to the elbow and damp darker patches on the shoulders, grey trousers, a brown leather belt and brown leather shoes, with a small stitched scar on his left forearm. Stylized 3D animated feature-film look: soft, rounded, appealing character design with expressive eyes, gentle subsurface skin shading, painterly cinematic lighting, shallow depth of field, subtle film grain.
```
**2b · Motion (image-to-video):**
```
They cross slowly; he matches her pace. She looks up at him and smiles.
```
**Caption in edit:** One small push travels further than you think.  
**Sound:** music resolves

### S18 · 4 s · macro, static

*Visual full stop, under the takeaway card.*  
Timeline 73–77 s · attach: nothing

**2a · Start frame (text-to-image, 9:16):**
```
Macro shot of a single raindrop falling into a clear puddle on asphalt, warm light reflected in the water. Stylized 3D animated feature-film look: soft, rounded, appealing character design with expressive eyes, gentle subsurface skin shading, painterly cinematic lighting, shallow depth of field, subtle film grain.
```
**2b · Motion (image-to-video):**
```
The drop hits and concentric ripples spread outward in slow motion until they fill the frame.
```
**Caption in edit:** ONE SMALL THING · Today, stop for someone the city walks past.  
**Sound:** single drop, last piano note

## Sound plan

- **Music:** Gentle solo piano or veena, enters at S10, swells at S12, resolves at S17. Royalty-free (YouTube Audio Library or a CC0 source).
- **Voice:** Only S11. Record a real child (with a parent's consent), or use a text-to-speech voice that handles Tamil, then sync it to the clip.
- **Ambience:** Continuous rain and OMR traffic bed under S01-S13; silence at S13; warm room tone in S14; softer rain from S15.
