import React from 'react';
import {AbsoluteFill, random} from 'remotion';
import {INTER, LORA, LORA_N} from './fonts';
import {Defs, HERO, ik, KID, Kid, KidHead, Man, Outfit, pose, Pose, V} from './rig';
import {Auto, Bike, BikeDefs, BlurDefs, Bus, Cam, Commuter, Drizzle, Grain, Hatchback, Placed, proj, Road, Roadside, Sedan, Sky, Towers} from './world';


const W = 1080;
const H = 1920;
const MAN_S = 0.95; // 1.72 m
const MAN_HIP = 375 * MAN_S;
const KID_HIP = 245;

// ---------------- shared helpers ----------------
export const Caption: React.FC<{text: string; sub?: string; y: number; size?: number; italic?: boolean; color?: string}> = ({text, sub, y, size = 60, italic, color = '#fbf7f0'}) => (
	<div style={{position: 'absolute', left: 70, right: 70, top: y, textAlign: 'center'}}>
		<div style={{fontFamily: italic ? LORA : LORA_N, fontStyle: italic ? 'italic' : 'normal', fontSize: size, lineHeight: 1.3, color, textShadow: '0 2px 22px rgba(0,0,0,0.55), 0 1px 3px rgba(0,0,0,0.5)'}}>{text}</div>
		{sub && <div style={{fontFamily: INTER, fontSize: size * 0.46, marginTop: 16, color: '#efe9df', letterSpacing: 0.5, textShadow: '0 1px 10px rgba(0,0,0,0.7)'}}>{sub}</div>}
	</div>
);
const Vignette: React.FC<{o?: number; col?: string}> = ({o = 0.55, col = '0,0,0'}) => (
	<AbsoluteFill style={{background: `radial-gradient(ellipse 75% 60% at 50% 48%, rgba(${col},0) 55%, rgba(${col},${o}) 100%)`}} />
);
const Slate: React.FC<{n: string; title: string}> = ({n, title}) => (
	<div style={{position: 'absolute', left: 36, top: 34, fontFamily: INTER, fontSize: 22, color: 'rgba(255,255,255,0.75)', letterSpacing: 2}}>
		{n} · {title.toUpperCase()}
	</div>
);

// rider sitting on the bike, solved with IK so hands meet the grips and feet meet the pegs
const RIDE_OFF: V = [-100, -372];
const toMan = (p: V): V => [(p[0] - RIDE_OFF[0]) / MAN_S, (p[1] - RIDE_OFF[1]) / MAN_S];
export const ridePose = (lean = 24): Pose => {
	const t = lean;
	const R = Math.PI / 180;
	const neckBase: V = [205 * Math.sin(t * R), -205 * Math.cos(t * R)];
	const sh: V = [neckBase[0] - 6 * Math.cos(t * R), neckBase[1] + 22];
	const grip = toMan([70, -476]);
	const peg = toMan([-34, -170]);
	const [ua, fa] = ik(sh, [grip[0] - 18, grip[1] + 4], 118, 108, 1);
	const [ua2, fa2] = ik([sh[0] - 10, sh[1] + 2], [grip[0] - 8, grip[1] - 2], 118, 108, 1);
	const [th, shn] = ik([6, 4], [peg[0] - 28, peg[1] - 34], 172, 168, -1);
	const [th2, sh2] = ik([-6, 2], [peg[0] - 40, peg[1] - 30], 172, 168, -1);
	return pose({t, neck: -10, head: -4, ua, fa, hand: -60, ua2, fa2, hand2: -60, th, sh: shn, foot: 0, th2, sh2, foot2: 0});
};
export const Rider: React.FC<{face?: object; wr?: number}> = ({face = {}, wr = 0}) => (
	<g>
		<Bike wr={wr} />
		<Man p={ridePose()} s={MAN_S} x={RIDE_OFF[0]} y={RIDE_OFF[1]} face={face} />
	</g>
);
const StandingMan: React.FC<{p?: Pose; o?: Outfit; face?: object; dir?: 1 | -1}> = ({p = pose(), o = HERO, face = {}, dir = 1}) => <Man p={p} o={o} face={face} s={MAN_S} y={-MAN_HIP} dir={dir} />;

const PEDS: Outfit[] = [
	{...HERO, shirt: '#a8325a', shirtShade: '#86244a', pants: '#e9dcc5', pantsShade: '#cdbfa6', kurta: true, helmet: false, scar: false, texture: false, wet: undefined, belt: undefined, umbrella: '#1e2330', mustache: false, skin: '#8f5f40', skinShade: '#704530', shoes: '#3a2a20'},
	{...HERO, shirt: '#e8e8e0', shirtShade: '#c9c9c0', pants: '#2e3340', pantsShade: '#22262f', helmet: false, scar: false, texture: false, wet: undefined, umbrella: '#262a30', skin: '#7d5236', skinShade: '#603c26'},
	{...HERO, shirt: '#2f6f73', shirtShade: '#245659', pants: '#d9cdb7', pantsShade: '#bfb39c', kurta: true, helmet: false, scar: false, texture: false, wet: undefined, belt: undefined, umbrella: '#5a2330', mustache: false, skin: '#94664a', skinShade: '#744c34'},
	{...HERO, shirt: '#5a6b4a', shirtShade: '#46553a', pants: '#3a3a3a', pantsShade: '#2b2b2b', helmet: false, scar: false, texture: false, wet: undefined, umbrella: '#1a1c20', skin: '#6f4a33', skinShade: '#553623'},
];
const UMB = pose({ua: 25, fa: 168, hand: 10});

// ===================================================================
// 0. CHARACTER SHEET
// ===================================================================
export const CharacterSheet: React.FC = () => {
	const ppm = 440;
	const s = ppm / 400;
	const ground = 1090;
	const note = (x: number, y: number, t: string, align: 'left' | 'right' = 'left') => (
		<div style={{position: 'absolute', left: align === 'left' ? x : undefined, right: align === 'right' ? W - x : undefined, top: y, fontFamily: INTER, fontSize: 21, color: '#3d342c', width: 300, textAlign: align, lineHeight: 1.35}}>{t}</div>
	);
	return (
		<AbsoluteFill style={{background: '#efe8dc'}}>
			<svg width={W} height={H}>
				<Defs />
				<BikeDefs />
				{new Array(40).fill(0).map((_, i) => <line key={i} x1={0} y1={i * 50} x2={W} y2={i * 50} stroke="#d9cfbf" strokeWidth={1} />)}
				{/* height ruler */}
				{[0, 0.5, 1, 1.5, 2].map((m) => (
					<g key={m}>
						<line x1={60} y1={ground - m * ppm} x2={1020} y2={ground - m * ppm} stroke="#b9ab96" strokeWidth={1} strokeDasharray="6 8" />
						<text x={64} y={ground - m * ppm - 8} fontFamily={INTER} fontSize={18} fill="#8b7b66">{m.toFixed(1)} m</text>
					</g>
				))}
				<ellipse cx={330} cy={ground + 4} rx={120} ry={14} fill="#000" opacity={0.12} />
				<g transform={`translate(330,${ground}) scale(${s})`}>
					<StandingMan p={pose({ua: 10, fa: 22, ua2: -6, fa2: 10, head: -2})} face={{brow: 0.2, smile: 0.2}} />
				</g>
				<ellipse cx={640} cy={ground + 4} rx={80} ry={12} fill="#000" opacity={0.12} />
				<g transform={`translate(640,${ground}) scale(${s})`}>
					<Kid p={pose({ua: 14, fa: 30, ua2: -4, fa2: 10, th: 3, sh: -1, th2: -4, sh2: -6, neck: 0, head: -8})} face={{smile: 1, look: 0.4}} y={-KID_HIP} dir={-1} />
				</g>
				{/* bike */}
				<g transform={`translate(540,1540) scale(0.8)`}>
					<Bike />
				</g>
				<line x1={0} y1={1545} x2={W} y2={1545} stroke="#cbbda8" strokeWidth={2} />
				{/* detail insets */}
				{[
					{cx: 150, label: 'Half helmet · stubble'},
					{cx: 540, label: 'The matching scar'},
					{cx: 930, label: 'Hood droplets · smile'},
				].map((c, i) => (
					<g key={i}>
						<clipPath id={`inset${i}`}><circle cx={c.cx} cy={1770} r={92} /></clipPath>
						<circle cx={c.cx} cy={1770} r={95} fill="#fff" stroke="#b9ab96" strokeWidth={3} />
						<g clipPath={`url(#inset${i})`}>
							<rect x={c.cx - 110} y={1670} width={220} height={220} fill={i === 1 ? '#d8cbb8' : '#c8d3dc'} />
							{i === 0 && <g transform={`translate(${c.cx - 16},${1770 + 286 * 1.9}) scale(1.9)`}><Man p={pose()} face={{brow: 0.2}} x={0} y={0} s={1} /></g>}
							{i === 1 && (
								<g>
									<g transform={`translate(${c.cx - 50},1700) rotate(-70) scale(2.6)`}>
										<path d="M -16 -20 L -12 80 L 12 80 L 16 -20 Z" fill={HERO.skin} />
										<g transform="translate(-4,10)"><path d="M 5 0 Q 7 13 6 26" stroke="#e5b49c" strokeWidth={3.4} fill="none" strokeLinecap="round" />{[5, 11, 17, 22].map((k) => <line key={k} x1={2} y1={k} x2={10} y2={k + 1} stroke="#d9a28a" strokeWidth={1.4} />)}</g>
									</g>
									<g transform={`translate(${c.cx + 40},1860) rotate(-70) scale(2.0)`}>
										<path d="M -12 -20 L -9 70 L 9 70 L 12 -20 Z" fill={KID.skin} />
										<g transform="translate(-4,10)"><path d="M 5 0 Q 7 13 6 26" stroke="#e5b49c" strokeWidth={3.4} fill="none" strokeLinecap="round" />{[5, 11, 17, 22].map((k) => <line key={k} x1={2} y1={k} x2={10} y2={k + 1} stroke="#d9a28a" strokeWidth={1.4} />)}</g>
									</g>
								</g>
							)}
							{i === 2 && <g transform={`translate(${c.cx - 26},${1770 + 104}) scale(1.75)`}><KidHead face={{smile: 1}} /></g>}
						</g>
						<text x={c.cx} y={1896} textAnchor="middle" fontFamily={INTER} fontSize={19} fill="#5b4e40">{c.label}</text>
					</g>
				))}
			</svg>
			<div style={{position: 'absolute', left: 40, top: 40, fontFamily: LORA_N, fontSize: 44, color: '#2f2720'}}>Unga Naala Mudiyum — character sheet</div>
			<div style={{position: 'absolute', left: 42, top: 104, fontFamily: INTER, fontSize: 20, color: '#7a6a58'}}>Look-dev v2 · proportions to scale (man 1.72 m, kid 1.28 m, bike 2.1 m long)</div>
			{note(745, 250, 'HIM · 35–38 · lean, mild brown skin. Half helmet, light stubble, moustache.')}
			{note(745, 400, 'Sky-blue textured shirt, sleeves rolled, damp at the shoulders and back.')}
			{note(745, 545, 'Scar on the forearm. Grey trousers, brown belt, brown shoes.')}
			{note(745, 700, 'THE KID · 7–8 · warm smile. Yellow raincoat, hood up, raindrops on the hood.')}
			{note(745, 870, 'White school uniform. Green bag in a rain cover. The same scar.')}
			<div style={{position: 'absolute', left: 60, right: 60, top: 1568, fontFamily: INTER, fontSize: 21, color: '#3d342c', textAlign: 'center'}}>THE BIKE · dark-blue dual-purpose commuter, white tank, black seat, fork gaiters, spoked wheels (no badges)</div>
		</AbsoluteFill>
	);
};

// ===================================================================
// 1. ESTABLISHING — OMR, the glass towers, drizzle
// ===================================================================
export const Cut1: React.FC = () => {
	const c: Cam = {f: 720, h: 1.6, horizon: 1290};
	const lights = [{x: -0.4, z: 7, col: '#fff1c8'}, {x: 5.6, z: 7, col: '#fff1c8'}, {x: 2.6, z: 10, col: '#fff1c8'}, {x: -3.6, z: 10, col: '#ff6a55'}];
	return (
		<AbsoluteFill>
			<svg width={W} height={H}>
				<Defs /><BikeDefs /><BlurDefs list={[[1, 0], [2, 0]]} />
				<Sky h={c.horizon} />
				<Towers c={c} haze={0.3} near={0.42} />
				<Roadside c={c} />
				{/* people on the footpath, the kid at the kerb waiting to cross */}
				<Placed c={c} x={-4.2} z={14.6}><StandingMan p={UMB} o={PEDS[0]} /></Placed>
				<Placed c={c} x={-3.1} z={14.2} flip><StandingMan p={UMB} o={PEDS[3]} /></Placed>
				<Placed c={c} x={4.6} z={14.8} flip><StandingMan p={UMB} o={PEDS[1]} /></Placed>
				<Placed c={c} x={6.2} z={13.9}><StandingMan p={UMB} o={PEDS[2]} /></Placed>
				<Placed c={c} x={1.6} z={12.9}><Kid p={pose({neck: -4, head: -6, ua: 4, fa: 8})} face={{smile: 0.2, look: 0.6}} y={-KID_HIP} dir={-1} /></Placed>
				<Road c={c} lights={lights} />
				{/* far lane */}
				<Placed c={c} x={-6.4} z={10}><Bus /></Placed>
				<Placed c={c} x={4.9} z={10}><Sedan color="#3a3e45" /></Placed>
				{/* near lane: our man arrives */}
				<Placed c={c} x={-1.6} z={7}><Rider /></Placed>
				<Placed c={c} x={4.6} z={7}><Commuter coat="#27324a" scooter="#8d9399" /></Placed>
				{/* foreground puddle mirroring the towers and the grey sky */}
				<defs>
					<clipPath id="pud1"><path d="M -40 1760 Q 120 1650 460 1668 Q 760 1640 1000 1700 Q 1140 1760 1100 1960 L -40 1960 Z" /></clipPath>
					<filter id="ripple" x="0" y="0" width="100%" height="100%">
						<feTurbulence type="fractalNoise" baseFrequency="0.004 0.06" numOctaves="2" seed="7" />
						<feDisplacementMap in="SourceGraphic" scale="26" />
					</filter>
				</defs>
				<g clipPath="url(#pud1)">
					<g filter="url(#ripple)" opacity={0.85}>
						<g transform={`translate(0,${1960 + 1290 - 760}) scale(1,-1)`}>
							<Sky h={c.horizon} />
							<Towers c={{...c, horizon: 1290}} haze={0.3} near={0.42} />
						</g>
					</g>
					<rect x={-40} y={1640} width={1180} height={320} fill="#2a3038" opacity={0.35} />
					{new Array(14).fill(0).map((_, i) => <ellipse key={i} cx={random('rp' + i) * 1080} cy={1700 + random('rq' + i) * 220} rx={10 + random('rr' + i) * 24} ry={3 + random('rr' + i) * 6} fill="none" stroke="#e8eef3" strokeOpacity={0.45} strokeWidth={1.5} />)}
				</g>
				<path d="M -40 1760 Q 120 1650 460 1668 Q 760 1640 1000 1700 Q 1140 1760 1100 1960" stroke="#1f2328" strokeWidth={4} fill="none" opacity={0.5} />
				<Drizzle n={320} seed="c1" len={24} opacity={0.32} />
				<Drizzle n={40} seed="c1n" len={40} opacity={0.25} near />
				<Grain amount={0.09} seed={1} />
			</svg>
			<Vignette o={0.45} />
			<Slate n="01" title="Establishing · OMR, near the glass towers" />
			<div style={{position: 'absolute', left: 0, right: 0, top: 250, textAlign: 'center', fontFamily: INTER, fontSize: 26, letterSpacing: 8, color: 'rgba(255,255,255,0.9)', textShadow: '0 2px 12px rgba(0,0,0,0.5)'}}>OMR · MONDAY · 8:40 AM</div>
		</AbsoluteFill>
	);
};

// ===================================================================
// 2. RIDING IN — tracking shot, background streaks, kid soft in the distance
// ===================================================================
export const Cut2: React.FC = () => {
	const c: Cam = {f: 2300, h: 1.05, horizon: 1080, x: 0};
	return (
		<AbsoluteFill>
			<svg width={W} height={H}>
				<Defs /><BikeDefs /><BlurDefs list={[[7, 16], [6, 0], [3, 22], [0, 10]]} />
				<Sky h={c.horizon} />
				<g style={{filter: 'url(#b_6_0)'}}><Towers c={c} haze={0.55} /></g>
				<Roadside c={c} blur={6} />
				<Placed c={c} x={-3.5} z={14.4} blur={7} motion={16}><StandingMan p={UMB} o={PEDS[1]} /></Placed>
				<Placed c={c} x={1.9} z={12.9} blur={6}><Kid p={pose({neck: -4, head: -6})} face={{smile: 0.2}} y={-KID_HIP} dir={-1} /></Placed>
				<Placed c={c} x={4.5} z={14.5} blur={7} motion={16}><StandingMan p={UMB} o={PEDS[2]} /></Placed>
				<Road c={c} lights={[{x: -2.5, z: 10, col: '#fff1c8'}, {x: 0.6, z: 6.5, col: '#fff1c8'}]} />
				<Placed c={c} x={-4.2} z={10} blur={3} motion={22}><Hatchback color="#7a1d24" /></Placed>
				<Placed c={c} x={4.8} z={10} blur={3} motion={22}><Bus body="#476e8a" /></Placed>
				{/* our man, sharp */}
				<Placed c={c} x={0} z={6.5}>
					<ellipse cx={0} cy={6} rx={420} ry={26} fill="#000" opacity={0.3} />
					<Rider wr={20} face={{brow: 0.4}} />
				</Placed>
				{/* spray from the rear wheel */}
				<Placed c={c} x={0} z={6.5} blur={0} motion={10}>
					{new Array(26).fill(0).map((_, i) => <circle key={i} cx={-380 - random('sp' + i) * 260} cy={-20 - random('sq' + i) * 150} r={3 + random('sr' + i) * 6} fill="#d5dee8" opacity={0.5} />)}
				</Placed>
				<Drizzle n={300} seed="c2" len={30} opacity={0.3} />
				<Drizzle n={45} seed="c2n" len={44} opacity={0.3} near />
				<Grain amount={0.09} seed={2} />
			</svg>
			<Vignette o={0.5} />
			<Slate n="02" title="Riding in · tracking shot" />
			<Caption text="His bike was always a little too heavy for him." y={330} size={56} />
		</AbsoluteFill>
	);
};

// ===================================================================
// 3. THE STARE — he stands; the city keeps moving
// ===================================================================
export const Cut3: React.FC = () => {
	const c: Cam = {f: 2500, h: 1.35, horizon: 1000};
	const worried = pose({t: 5, neck: 14, head: 10, ua: 8, fa: 26, hand: 6, ua2: 14, fa2: 40, th: 6, sh: 0, th2: -6, sh2: -8});
	return (
		<AbsoluteFill>
			<svg width={W} height={H}>
				<Defs /><BikeDefs /><BlurDefs list={[[5, 0], [3, 36], [9, 0], [12, 0]]} />
				<Sky h={c.horizon} />
				<g style={{filter: 'url(#b_9_0)'}}><Towers c={c} haze={0.55} /></g>
				<Roadside c={c} blur={5} />
				{/* onlookers: they stop and stare */}
				<Placed c={c} x={-1.9} z={14} blur={5}><StandingMan p={pose({...UMB, neck: 10, head: 8})} o={PEDS[0]} /></Placed>
				<Placed c={c} x={-0.6} z={14.6} blur={5}><StandingMan p={pose({...UMB, neck: 10, head: 6})} o={PEDS[1]} /></Placed>
				<Placed c={c} x={1.9} z={14.2} blur={5} flip><StandingMan p={pose({...UMB, neck: 12, head: 10})} o={PEDS[3]} /></Placed>
				<Placed c={c} x={1.15} z={12.8} blur={5}><Kid p={pose({neck: 6, head: 6})} face={{smile: 0, look: 0.8}} y={-KID_HIP} dir={-1} /></Placed>
				<Road c={c} lights={[{x: -2.2, z: 9.8, col: '#fff1c8'}, {x: 2, z: 9.8, col: '#ff6a55'}]} />
				{/* traffic streaking past behind him */}
				<Placed c={c} x={-2.4} z={9.8} blur={3} motion={36}><Sedan color="#d8d8d6" /></Placed>
				<Placed c={c} x={2.9} z={9.8} blur={3} motion={36}><Commuter coat="#4a2a2a" scooter="#2c3e50" /></Placed>
				{/* him: damp, mud on the knee, looking around */}
				<Placed c={c} x={0.15} z={6.2}>
					<ellipse cx={0} cy={4} rx={150} ry={18} fill="#000" opacity={0.3} />
					<StandingMan p={worried} o={{...HERO, mud: true} as Outfit} face={{brow: 1, smile: -0.6, look: -0.6}} dir={-1} />
				</Placed>
				{/* the fallen bike, foreground, out of focus */}
				<Placed c={c} x={-0.9} z={4.3} blur={12}>
					<g transform="scale(1,0.34) rotate(-4)"><Bike light={false} /></g>
				</Placed>
				<Drizzle n={280} seed="c3" len={28} opacity={0.3} />
				<Drizzle n={40} seed="c3n" len={44} opacity={0.3} near />
				<Grain amount={0.09} seed={3} />
			</svg>
			<Vignette o={0.55} />
			<Slate n="03" title="The stare · everyone sees, no one stops" />
			<Caption text="But the whole city saw… and kept moving." y={300} size={56} />
		</AbsoluteFill>
	);
};

// ===================================================================
// 4. TWO SCARS — close-up on the third try
// ===================================================================
const ForearmCU: React.FC<{a: V; b: V; w0: number; w1: number; skin: string; shade: string; scarAt: number; sleeve?: string; sleeveShade?: string; adult?: boolean}> = ({a, b, w0, w1, skin, shade, scarAt, sleeve, sleeveShade, adult}) => {
	const len = Math.hypot(b[0] - a[0], b[1] - a[1]);
	const ang = (Math.atan2(b[1] - a[1], b[0] - a[0]) * 180) / Math.PI - 90;
	return (
		<g transform={`translate(${a[0]},${a[1]}) rotate(${ang})`}>
			<path d={`M ${-w0 / 2} 0 Q ${-w0 / 2 - 8} ${len * 0.4} ${-w1 / 2} ${len} L ${w1 / 2} ${len} Q ${w0 / 2 + 10} ${len * 0.4} ${w0 / 2} 0 Z`} fill={skin} />
			<path d={`M ${-w0 / 2} 0 Q ${-w0 / 2 - 8} ${len * 0.4} ${-w1 / 2} ${len} L ${w1 / 2} ${len} Q ${w0 / 2 + 10} ${len * 0.4} ${w0 / 2} 0 Z`} fill="url(#lit)" />
			<path d={`M ${w0 * 0.25} 10 Q ${w0 * 0.3} ${len * 0.5} ${w1 * 0.3} ${len - 10}`} stroke={shade} strokeWidth={w0 * 0.12} fill="none" opacity={0.35} />
			{adult && new Array(26).fill(0).map((_, i) => {
				const yy = 30 + random('hair' + i) * (len - 60);
				const xx = (random('hx' + i) - 0.5) * w0 * 0.8;
				return <line key={i} x1={xx} y1={yy} x2={xx + 4} y2={yy + 10} stroke="#2a1a12" strokeWidth={1.2} opacity={0.35} />;
			})}
			{/* scar */}
			<g transform={`translate(${-w0 * 0.12},${len * scarAt}) rotate(-12)`}>
				<path d={`M 0 0 Q ${w0 * 0.06} ${w0 * 0.35} 0 ${w0 * 0.7}`} stroke="#e8b9a2" strokeWidth={w0 * 0.075} fill="none" strokeLinecap="round" />
				<path d={`M 3 2 Q ${w0 * 0.06 + 3} ${w0 * 0.35} 3 ${w0 * 0.7}`} stroke="#7d4834" strokeWidth={w0 * 0.02} fill="none" opacity={0.5} />
				{[0.12, 0.28, 0.44, 0.6].map((k) => <line key={k} x1={-w0 * 0.07} y1={w0 * k} x2={w0 * 0.1} y2={w0 * k + 4} stroke="#d9a08a" strokeWidth={w0 * 0.025} strokeLinecap="round" />)}
			</g>
			{/* beads of rain on skin */}
			{new Array(adult ? 9 : 6).fill(0).map((_, i) => {
				const yy = 20 + random((adult ? 'ad' : 'kd') + i) * (len - 40);
				const xx = (random((adult ? 'ax' : 'kx') + i) - 0.5) * w0 * 0.7;
				const r = 4 + random((adult ? 'ar' : 'kr') + i) * 6;
				return <g key={'d' + i}><circle cx={xx} cy={yy} r={r} fill="#fff" fillOpacity={0.22} /><circle cx={xx - r * 0.3} cy={yy - r * 0.35} r={r * 0.3} fill="#fff" fillOpacity={0.9} /></g>;
			})}
			{sleeve && (
				<g>
					<path d={`M ${-w0 / 2 - 22} -200 L ${-w0 / 2 - 16} 40 Q 0 58 ${w0 / 2 + 16} 40 L ${w0 / 2 + 22} -200 Z`} fill={sleeve} />
					<path d={`M ${-w0 / 2 - 22} -200 L ${-w0 / 2 - 16} 40 Q 0 58 ${w0 / 2 + 16} 40 L ${w0 / 2 + 22} -200 Z`} fill="url(#lit)" />
					<path d={`M ${-w0 / 2 - 16} 22 Q 0 40 ${w0 / 2 + 16} 22`} stroke={sleeveShade} strokeWidth={5} fill="none" />
					<path d={`M ${-w0 / 2 - 16} 4 Q 0 22 ${w0 / 2 + 16} 4`} stroke={sleeveShade} strokeWidth={3} fill="none" opacity={0.6} />
				</g>
			)}
		</g>
	);
};
// back of a hand: grip = fingers curled over an edge; flat = fingers spread pressing
const HandCU: React.FC<{at: V; ang: number; s: number; skin: string; shade: string; grip?: boolean}> = ({at, ang, s, skin, shade, grip}) => (
	<g transform={`translate(${at[0]},${at[1]}) rotate(${ang}) scale(${s})`}>
		{/* thumb */}
		<path d="M -40 18 Q -78 44 -74 92 Q -70 110 -56 104 Q -52 70 -30 52 Z" fill={skin} />
		<path d="M -40 18 Q -78 44 -74 92 Q -70 110 -56 104 Q -52 70 -30 52 Z" fill="url(#lit)" />
		{/* back of hand */}
		<path d="M -44 -4 Q -52 50 -44 96 L 46 98 Q 54 50 44 -4 Z" fill={skin} />
		<path d="M -44 -4 Q -52 50 -44 96 L 46 98 Q 54 50 44 -4 Z" fill="url(#lit)" />
		<path d="M -18 10 Q -14 50 -22 88 M 8 14 Q 4 50 10 90" stroke={shade} strokeWidth={3} fill="none" opacity={0.35} />
		{/* fingers */}
		{(grip ? [[-33, 0, 46], [-11, 0, 52], [11, 0, 50], [32, 0, 40]] : [[-34, -10, 92], [-12, -3, 104], [11, 3, 100], [32, 10, 80]]).map(([fx, fa, fl], i) => (
			<g key={i} transform={`translate(${fx},${92}) rotate(${fa})`}>
				<rect x={-11} y={-6} width={22} height={fl} rx={11} fill={skin} />
				<rect x={-11} y={-6} width={22} height={fl} rx={11} fill="url(#lit)" />
				<path d={`M -7 ${fl * 0.45} Q 0 ${fl * 0.45 + 4} 7 ${fl * 0.45}`} stroke={shade} strokeWidth={2} fill="none" opacity={0.6} />
				{!grip && <rect x={-7} y={fl - 22} width={14} height={14} rx={6} fill="#e2b8a2" opacity={0.85} />}
				<ellipse cx={0} cy={2} rx={10} ry={6} fill="#fff" opacity={0.12} />
			</g>
		))}
		{grip && <path d="M -46 140 Q 0 152 46 136" stroke={shade} strokeWidth={4} fill="none" opacity={0.5} />}
	</g>
);
export const Cut4: React.FC = () => (
	<AbsoluteFill>
		<svg width={W} height={H}>
			<Defs /><BikeDefs />
			<defs>
				<linearGradient id="cu4bg" x1="0" y1="0" x2="0" y2="1">
					<stop offset="0" stopColor="#58626e" />
					<stop offset="0.5" stopColor="#3c434c" />
					<stop offset="1" stopColor="#25292f" />
				</linearGradient>
				<filter id="bk" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="22" /></filter>
				<filter id="bk2" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="5" /></filter>
			</defs>
			<rect width={W} height={H} fill="url(#cu4bg)" />
			{/* out-of-focus street: kerb stripes, headlights, tail lights */}
			<g filter="url(#bk)">
				{new Array(9).fill(0).map((_, i) => <rect key={i} x={i * 140 - 60} y={520} width={140} height={60} fill={i % 2 ? '#d8b43a' : '#1b1c1f'} opacity={0.8} />)}
				<rect x={0} y={260} width={W} height={260} fill="#5b7058" opacity={0.6} />
				<rect x={-40} y={1220} width={1160} height={700} fill="#2b2f35" />
			</g>
			{[[160, 760, 70, '#fff0c4'], [930, 690, 56, '#fff0c4'], [880, 1280, 44, '#ff6a55'], [300, 1450, 36, '#ff7a5a'], [700, 470, 40, '#fbe7b5'], [80, 1180, 30, '#fff0c4']].map(([x, y, r, col], i) => (
				<circle key={i} cx={x as number} cy={y as number} r={r as number} fill={col as string} opacity={0.45} filter="url(#bk2)" />
			))}
			{/* the bike, close, tilted up mid-lift */}
			<g transform="translate(600,1060) rotate(-16) scale(3.1) translate(-40,370)">
				<Bike light={false} />
			</g>
			{/* his arm from the top right, gripping the tank edge */}
			<ForearmCU a={[1180, 200]} b={[780, 770]} w0={140} w1={104} skin={HERO.skin} shade={HERO.skinShade} scarAt={0.42} sleeve={HERO.shirt} sleeveShade={HERO.shirtShade} adult />
			<HandCU at={[780, 770]} ang={35} s={1.55} skin={HERO.skin} shade={HERO.skinShade} grip />
			{/* the kid's small arm from the bottom left, pushing flat on the side panel */}
			<ForearmCU a={[-60, 1780]} b={[380, 1260]} w0={96} w1={74} skin={KID.skin} shade={KID.shade} scarAt={0.5} sleeve={KID.coat} sleeveShade={KID.coatShade} />
			<HandCU at={[380, 1260]} ang={-140} s={1.12} skin={KID.skin} shade={KID.shade} />
			<Drizzle n={120} seed="c4" len={40} opacity={0.35} />
			<Drizzle n={30} seed="c4n" len={60} opacity={0.3} near />
			<Grain amount={0.1} seed={4} />
		</svg>
		<Vignette o={0.6} />
		<Slate n="04" title="Two scars · the third try" />
	</AbsoluteFill>
);

// ===================================================================
// 5. "UNGA NAALA MUDIYUM" — the kid, close
// ===================================================================
export const Cut5: React.FC = () => {
	const c: Cam = {f: 1700, h: 1.0, horizon: 930};
	return (
		<AbsoluteFill>
			<svg width={W} height={H}>
				<Defs /><BikeDefs /><BlurDefs list={[[14, 0], [22, 0]]} />
				<Sky h={c.horizon} />
				<g style={{filter: 'url(#b_14_0)'}}>
					<Towers c={c} haze={0.6} />
				</g>
				<Roadside c={c} blur={14} />
				<g style={{filter: 'url(#b_14_0)'}}><Road c={c} /></g>
				<Placed c={c} x={-3} z={10} blur={14}><Sedan color="#3a3e45" /></Placed>
				{/* him, huge and soft, at the right edge */}
				<Placed c={c} x={1.9} z={3.0} blur={22}><StandingMan p={pose({t: 20, ua: 40, fa: 60})} dir={-1} /></Placed>
				{[[120, 840, 50, '#fff0c4'], [300, 900, 34, '#ff6a55'], [960, 980, 40, '#fff0c4']].map(([x, y, r, col], i) => (
					<circle key={i} cx={x as number} cy={y as number} r={r as number} fill={col as string} opacity={0.4} style={{filter: 'blur(6px)'}} />
				))}
				{/* the kid */}
				<g transform="translate(500,1930) scale(4.3)">
					<Kid p={pose({t: -6, neck: -10, head: -12, ua: 30, fa: 50, ua2: 24, fa2: 44})} face={{smile: 1, open: 0.7, look: 1}} />
				</g>
				<Drizzle n={160} seed="c5" len={36} opacity={0.3} />
				<Drizzle n={36} seed="c5n" len={60} opacity={0.35} near />
				<Grain amount={0.09} seed={5} />
			</svg>
			<AbsoluteFill style={{background: 'linear-gradient(180deg, rgba(0,0,0,0) 62%, rgba(10,12,16,0.55) 82%, rgba(10,12,16,0.7) 100%)'}} />
			<Vignette o={0.45} />
			<Slate n="05" title="Unga naala mudiyum" />
			<Caption text="“Come on anna, unga naala mudiyum!”" sub="Come on, brother. You can do it." y={1480} size={62} italic color="#ffe39a" />
		</AbsoluteFill>
	);
};

// ===================================================================
// 6. THE MEMORY — warm, glowing, remembered (the Ratatouille-style flashback)
// ===================================================================
const Bicycle: React.FC = () => (
	<g stroke="#141414" fill="none" strokeLinecap="round" strokeLinejoin="round">
		{[-230, 230].map((x) => (
			<g key={x} transform={`translate(${x},-140)`}>
				<circle r={134} strokeWidth={12} />
				<circle r={124} strokeWidth={3} stroke="#a8a8a8" />
				{new Array(16).fill(0).map((_, i) => <line key={i} x1={0} y1={0} x2={Math.cos(i * 0.3927) * 122} y2={Math.sin(i * 0.3927) * 122} strokeWidth={1.4} stroke="#9a9a9a" />)}
				<path d="M -150 -30 A 152 152 0 0 1 120 -96" strokeWidth={10} stroke="#1a1a1a" />
			</g>
		))}
		<path d="M -230 -140 L 0 -130 L -40 -430 Z M -40 -410 L 180 -420 L 0 -130 M 180 -420 L 230 -140" strokeWidth={16} />
		<path d="M 180 -420 L 170 -480 Q 150 -500 100 -494 L 70 -490" strokeWidth={10} />
		<path d="M -90 -460 Q -40 -478 10 -458 L -30 -440 Z" fill="#3b2a1e" stroke="#3b2a1e" strokeWidth={6} />
		<path d="M -300 -300 L -60 -300 M -280 -300 L -230 -140" strokeWidth={8} />
		<path d="M -40 -150 L -220 -150" strokeWidth={22} stroke="#2a2a2a" />
	</g>
);
export const Cut6: React.FC = () => {
	const c: Cam = {f: 1600, h: 0.9, horizon: 1040};
	const oldMan: Outfit = {...HERO, shirt: '#f2efe6', shirtShade: '#d8d2c3', pants: '#f2efe6', pantsShade: '#ddd6c6', shoes: '#4a3424', helmet: false, hair: '#d9d5ce', scar: false, texture: false, wet: undefined, belt: undefined, skin: '#8a5a3c', skinShade: '#6a4229', mustache: true};
	const scene = (
		<g>
			<defs>
				<linearGradient id="warmSky" x1="0" y1="0" x2="0" y2="1">
					<stop offset="0" stopColor="#f3c98a" />
					<stop offset="1" stopColor="#fbe6bf" />
				</linearGradient>
				<radialGradient id="sun" cx="0.5" cy="0.5" r="0.5">
					<stop offset="0" stopColor="#fffbe8" />
					<stop offset="0.4" stopColor="#ffe9b0" stopOpacity="0.8" />
					<stop offset="1" stopColor="#ffd98a" stopOpacity="0" />
				</radialGradient>
			</defs>
			<rect x={-100} y={-100} width={1280} height={c.horizon + 120} fill="url(#warmSky)" />
			{/* temple tower far away in the haze */}
			{(() => {
				const p = proj(c, -14, 240);
				const s = p.ppm;
				const tiers = new Array(7).fill(0).map((_, i) => {
					const w = (16 - i * 1.8) * s;
					const hh = 5 * s;
					return <rect key={i} x={p.sx - w / 2} y={p.sy - (i + 1) * hh} width={w} height={hh} fill="#d9a873" stroke="#c99560" strokeWidth={1} />;
				});
				return <g opacity={0.75}>{tiers}<path d={`M ${p.sx - 3 * s} ${p.sy - 35 * s} Q ${p.sx} ${p.sy - 40 * s} ${p.sx + 3 * s} ${p.sy - 35 * s} Z`} fill="#d9a873" /></g>;
			})()}
			<circle cx={830} cy={640} r={330} fill="url(#sun)" />
			{/* coconut palms */}
			{[[-6, 40, 14], [4, 55, 16], [9, 30, 12]].map(([x, z, h], i) => {
				const b = proj(c, x, z);
				const t = proj(c, x + 1.2, z, h);
				return (
					<g key={i} opacity={0.85}>
						<path d={`M ${b.sx} ${b.sy} Q ${b.sx + 0.2 * b.ppm} ${(b.sy + t.sy) / 2} ${t.sx} ${t.sy}`} stroke="#8a6a44" strokeWidth={0.4 * b.ppm} fill="none" />
						{new Array(9).fill(0).map((_, k) => {
							const a = (k / 9) * Math.PI * 2;
							const l = 4.2 * b.ppm;
							return <path key={k} d={`M ${t.sx} ${t.sy} Q ${t.sx + Math.cos(a) * l * 0.6} ${t.sy + Math.sin(a) * l * 0.3 - 0.8 * b.ppm} ${t.sx + Math.cos(a) * l} ${t.sy + Math.abs(Math.sin(a)) * l * 0.5 + 0.6 * b.ppm}`} stroke="#6f8a4a" strokeWidth={0.5 * b.ppm} fill="none" strokeLinecap="round" />;
						})}
					</g>
				);
			})}
			{/* small-town houses with tiled roofs */}
			{[[-7.5, '#e6b77a'], [-2.5, '#c9d3c1'], [2.5, '#e8c3a8'], [7.5, '#e2c98f']].map(([x, col], i) => {
				const zb = 13;
				const a = proj(c, (x as number) - 2.4, zb);
				const b = proj(c, (x as number) + 2.4, zb);
				const top = proj(c, x as number, zb, 3.2);
				const roof = proj(c, x as number, zb, 4.8);
				const s = a.ppm;
				return (
					<g key={i}>
						<rect x={a.sx} y={top.sy} width={b.sx - a.sx} height={a.sy - top.sy} fill={col as string} />
						<path d={`M ${a.sx - 0.4 * s} ${top.sy} L ${(a.sx + b.sx) / 2} ${roof.sy} L ${b.sx + 0.4 * s} ${top.sy} Z`} fill="#b05a38" />
						{new Array(6).fill(0).map((_, k) => <line key={k} x1={a.sx + ((k + 0.5) * (b.sx - a.sx)) / 6} y1={top.sy - ((roof.sy - top.sy) * -0.15)} x2={(a.sx + b.sx) / 2} y2={roof.sy} stroke="#8e4529" strokeWidth={1} opacity={0.5} />)}
						<rect x={a.sx + 0.4 * s} y={top.sy + 0.2 * s} width={(b.sx - a.sx) - 0.8 * s} height={0.25 * s} fill="#000" opacity={0.15} />
						{[0.8, 2.4, 4.0].map((px) => <rect key={px} x={a.sx + px * s} y={top.sy + 0.3 * s} width={0.16 * s} height={a.sy - top.sy - 0.3 * s} fill="#f4ecdc" />)}
						<rect x={a.sx + 1.6 * s} y={top.sy + 1.0 * s} width={0.9 * s} height={a.sy - top.sy - 1.0 * s} fill="#6b4a32" />
						<rect x={a.sx - 0.2 * s} y={a.sy - 0.5 * s} width={(b.sx - a.sx) + 0.4 * s} height={0.5 * s} fill="#d8c4a2" />
					</g>
				);
			})}
			{/* dusty lane */}
			<rect x={-100} y={proj(c, 0, 12.5).sy} width={1280} height={1200} fill="#d9b27e" />
			<rect x={-100} y={proj(c, 0, 12.5).sy} width={1280} height={1200} fill="url(#litV)" opacity={0.6} />
			{/* the old man and the boy lifting the fallen bicycle */}
			<Placed c={c} x={0.15} z={4.6}><ellipse cx={0} cy={4} rx={620} ry={40} fill="#8a5a2c" opacity={0.25} /></Placed>
			<Placed c={c} x={0.5} z={4.6}>
				<g transform="scale(1,0.62) rotate(-6)"><Bicycle /></g>
			</Placed>
			<Placed c={c} x={1.55} z={4.6}>
				<Man p={pose({t: 48, neck: -16, head: -6, ua: 50, fa: 40, ua2: 44, fa2: 36, th: 22, sh: -10, th2: 12, sh2: -16})} o={oldMan} face={{smile: 0.8, brow: -0.2, look: -0.6}} s={MAN_S * 0.96} y={-MAN_HIP * 0.88} dir={-1} />
			</Placed>
			<Placed c={c} x={-0.55} z={4.4}>
				<Kid p={pose({t: 30, neck: -14, head: -10, ua: 62, fa: 70, ua2: 56, fa2: 66, th: 18, sh: -12, th2: 4, sh2: -18})} face={{smile: 1, look: 1}} y={-KID_HIP * 0.93} raincoat={false} bagCover={false} />
			</Placed>
			{/* dust in the sunlight */}
			{new Array(70).fill(0).map((_, i) => (
				<circle key={i} cx={random('mx' + i) * W} cy={300 + random('my' + i) * 1300} r={1.5 + random('mr' + i) * 4} fill="#fff4d6" opacity={0.25 + random('mo' + i) * 0.5} />
			))}
		</g>
	);
	return (
		<AbsoluteFill style={{background: '#f6dcae'}}>
			<svg width={W} height={H}>
				<Defs /><BikeDefs />
				{scene}
				{/* bloom: a blurred, brightened copy laid over itself */}
				<g style={{filter: 'blur(26px) brightness(1.25)', mixBlendMode: 'screen'}} opacity={0.55}>{scene}</g>
				{/* light shafts from the sun */}
				<g style={{filter: 'blur(18px)'}} opacity={0.35}>
					{[-30, -14, 2, 18, 34].map((a, i) => (
						<path key={i} d={`M 830 640 L ${830 + Math.cos(((a + 110) * Math.PI) / 180) * 2200 - 60} ${640 + Math.sin(((a + 110) * Math.PI) / 180) * 2200} L ${830 + Math.cos(((a + 110) * Math.PI) / 180) * 2200 + 60} ${640 + Math.sin(((a + 110) * Math.PI) / 180) * 2200} Z`} fill="#fff1c8" />
					))}
				</g>
				<rect width={W} height={H} fill="#ff9d3a" opacity={0.12} style={{mixBlendMode: 'multiply'}} />
				<Grain amount={0.12} seed={6} />
			</svg>
			{/* soft, dreamy edges */}
			<AbsoluteFill style={{background: 'radial-gradient(ellipse 70% 58% at 50% 52%, rgba(255,236,200,0) 55%, rgba(255,226,180,0.85) 100%)'}} />
			<Slate n="06" title="The memory · warm, glowing, remembered" />
			<Caption text="He remembered a boy who used to stop for strangers." y={300} size={54} italic color="#4a2e18" />
		</AbsoluteFill>
	);
};
