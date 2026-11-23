import React, {useMemo} from 'react';
import {AbsoluteFill, Easing, random, Sequence, useCurrentFrame} from 'remotion';
import {Bike, Caption, Car, kf, P, Person, POSES, poseAt, Rain, walkPose} from './lib';

const GY = 1385; // ground line of the rider's lane
const BACK_WALK = 1135; // back sidewalk ground

// ================= the city: background =================
const City: React.FC = () => {
	const far = useMemo(() => new Array(11).fill(0).map((_, i) => ({x: i * 105 - 40, w: 90 + random('fw' + i) * 60, h: 380 + random('fh' + i) * 330})), []);
	const near = useMemo(() => new Array(8).fill(0).map((_, i) => ({x: i * 150 - 60, w: 130 + random('nw' + i) * 50, h: 280 + random('nh' + i) * 320})), []);
	return (
		<g>
			<defs>
				<linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
					<stop offset="0" stopColor="#6f7d90" />
					<stop offset="1" stopColor="#b9c1ca" />
				</linearGradient>
				<linearGradient id="road" x1="0" y1="0" x2="0" y2="1">
					<stop offset="0" stopColor="#4a4f58" />
					<stop offset="0.5" stopColor="#3a3e46" />
					<stop offset="1" stopColor="#30333a" />
				</linearGradient>
				<linearGradient id="fog" x1="0" y1="0" x2="0" y2="1">
					<stop offset="0" stopColor="#c9d0d8" stopOpacity="0" />
					<stop offset="1" stopColor="#c9d0d8" stopOpacity="0.75" />
				</linearGradient>
			</defs>
			<rect x={-200} y={-200} width={1480} height={1400} fill="url(#sky)" />
			{far.map((b, i) => (
				<rect key={i} x={b.x} y={1060 - b.h} width={b.w} height={b.h} fill="#7d8796" />
			))}
			<rect x={-200} y={600} width={1480} height={460} fill="url(#fog)" />
			{near.map((b, i) => (
				<g key={i}>
					<rect x={b.x} y={1060 - b.h} width={b.w} height={b.h} fill="#525a68" />
					{new Array(Math.floor(b.h / 55)).fill(0).map((_, r) =>
						[0, 1, 2].map((c) => (
							<rect key={r + '-' + c} x={b.x + 16 + c * (b.w - 30) / 3} y={1060 - b.h + 22 + r * 55} width={(b.w - 60) / 3} height={26} fill={random(`win${i}-${r}-${c}`) > 0.62 ? '#f1cf8f' : '#3f4653'} opacity={0.85} />
						)),
					)}
				</g>
			))}
			{/* back sidewalk */}
			<rect x={-200} y={1040} width={1480} height={105} fill="#646b77" />
			<rect x={-200} y={1140} width={1480} height={14} fill="#8a909a" />
			{/* road */}
			<rect x={-200} y={1154} width={1480} height={500} fill="url(#road)" />
			{new Array(14).fill(0).map((_, i) => <rect key={i} x={i * 110 - 160} y={1300} width={60} height={7} fill="#d9d9d2" opacity={0.6} />)}
			{/* wet reflections */}
			{new Array(9).fill(0).map((_, i) => (
				<ellipse key={i} cx={random('pr' + i) * 1200 - 60} cy={1340 + random('py' + i) * 280} rx={60 + random('px' + i) * 90} ry={7} fill="#8e9aab" opacity={0.25} />
			))}
			{/* pothole */}
			<ellipse cx={560} cy={GY + 2} rx={48} ry={11} fill="#22252b" />
			<ellipse cx={556} cy={GY} rx={34} ry={6} fill="#6c7a8d" opacity={0.6} />
			{/* front sidewalk */}
			<rect x={-200} y={1648} width={1480} height={14} fill="#8a909a" />
			<rect x={-200} y={1660} width={1480} height={400} fill="#555c68" />
		</g>
	);
};

// ================= traffic =================
const useTraffic = () =>
	useMemo(
		() =>
			new Array(48).fill(0).map((_, i) => {
				const farLane = i % 2 === 0;
				const r = random('car' + i);
				const kind = r > 0.82 ? 2 : r > 0.62 ? 1 : 0;
				return {
					f0: i * 26 + random('cf' + i) * 18 - 40,
					v: kind === 2 ? 5 : 7 + random('cv' + i) * 5,
					dir: farLane ? -1 : 1,
					y: farLane ? 1215 : 1290,
					s: farLane ? 0.62 : 0.78,
					color: ['#6b7f99', '#a34b4b', '#d8d8d8', '#2f3b4a', '#8a8f96', '#5f7a6a'][i % 6],
					kind,
					busColor: ['#2f6db0', '#b84a3a'][i % 2],
				};
			}),
		[],
	);
const Traffic: React.FC<{lane: 'far' | 'mid'}> = ({lane}) => {
	const f = useCurrentFrame();
	const cars = useTraffic();
	return (
		<g>
			{cars
				.filter((c) => (lane === 'far' ? c.dir === -1 : c.dir === 1))
				.map((c, i) => {
					const x = c.dir === 1 ? -400 + (f - c.f0) * c.v : 1480 - (f - c.f0) * c.v;
					if (f < c.f0 || x < -500 || x > 1600) return null;
					return <Car key={i} x={x} y={c.y} s={c.s} dir={c.dir} color={c.kind === 2 ? c.busColor : c.color} kind={c.kind} />;
				})}
		</g>
	);
};

// ================= pedestrians on the back sidewalk (they slow down to look, then move on) =================
const Pedestrians: React.FC = () => {
	const f = useCurrentFrame();
	const peds = useMemo(
		() =>
			new Array(14).fill(0).map((_, i) => ({
				dir: i % 2 === 0 ? 1 : -1,
				f0: i * 85 - 200 + random('pf' + i) * 40,
				v: 2.2 + random('pv' + i) * 1.2,
				tint: ['#4d5562', '#6a5a4a', '#3f5a66', '#5c4c5e'][i % 4],
			})),
		[],
	);
	return (
		<g>
			{peds.map((p, i) => {
				const start = p.dir === 1 ? -150 : 1230;
				const look = 760; // where the fallen man is
				let t = f - p.f0;
				if (t < 0) return null;
				const tReach = Math.abs(look - start) / p.v;
				const pause = f > 420 && f < 760 ? 30 : 0; // only stop to stare after the fall
				let moving = true;
				if (pause && t > tReach && t < tReach + pause) {
					t = tReach;
					moving = false;
				} else if (pause && t >= tReach + pause) t -= pause;
				const x = start + p.dir * p.v * t;
				if (x < -200 || x > 1300) return null;
				const pose = moving ? walkPose(f * 0.18 + i, POSES.umbrella) : P({...POSES.umbrella, head: 12});
				return <Person key={i} x={x} y={BACK_WALK - 82} s={0.55} dir={p.dir} pose={pose} look="ped" tint={p.tint} umbrella />;
			})}
		</g>
	);
};

// ================= the main city scene =================
const BIKE_X = (f: number) => kf(f, [150, 330, 365], [-250, 520, 600], Easing.out(Easing.quad));

const CityScene: React.FC = () => {
	const f = useCurrentFrame();

	// ---- bike ----
	const bx = BIKE_X(f);
	const bump = f >= 330 && f < 342 ? -Math.sin(((f - 330) / 12) * Math.PI) * 18 : 0;
	const bikeRot = kf(f, [330, 336, 342], [0, -7, 0]);
	const sy = (() => {
		if (f < 340) return 1;
		if (f < 700) return kf(f, [340, 365], [1, 0.3], Easing.in(Easing.quad));
		if (f < 790) return kf(f, [725, 755, 768], [0.3, 0.55, 0.3]);
		if (f < 880) return kf(f, [815, 848, 860], [0.3, 0.62, 0.3]);
		const tremble = f > 950 && f < 990 ? Math.sin(f * 1.3) * 0.015 : 0;
		return kf(f, [905, 950, 990, 1050], [0.3, 0.5, 0.5, 1]) + tremble;
	})();
	const wheelRot = bx * 1.1;

	// ---- man ----
	let man: {x: number; y: number; rot: number; dir: number; pose: ReturnType<typeof poseAt>; smile: number};
	if (f < 330) {
		man = {x: bx - 45, y: GY - 185 + bump, rot: 0, dir: 1, pose: POSES.ride, smile: 0};
	} else if (f < 425) {
		man = {
			x: kf(f, [330, 345, 360, 372], [bx - 45, 620, 720, 770]),
			y: kf(f, [330, 345, 360, 372], [GY - 185, GY - 250, GY - 130, GY - 22]),
			rot: kf(f, [330, 345, 372], [0, 35, 90]),
			dir: 1,
			pose: poseAt(f, [[330, POSES.ride], [365, POSES.stand]]),
			smile: -0.6,
		};
	} else {
		const x = kf(f, [425, 490, 700, 725, 760, 790, 815, 848, 880, 905, 990, 1050], [770, 800, 800, 826, 805, 826, 800, 826, 826, 826, 826, 787]);
		const y = kf(f, [425, 455, 490], [GY - 22, GY - 38, GY - 150]);
		const rot = kf(f, [425, 455], [90, 0]);
		const dir = f < 600 ? 1 : f < 640 ? -1 : f < 680 ? 1 : -1;
		const dustWave = f > 490 && f < 560 ? Math.sin((f - 490) * 0.5) * 25 : 0;
		const tl: [number, typeof POSES.stand][] = [
			[425, POSES.stand], [455, POSES.sit], [490, POSES.stand],
			[500, POSES.dust], [550, POSES.dust], [565, POSES.stand], [690, POSES.sad],
			[700, POSES.sad], [725, POSES.bend], [755, POSES.lift], [790, POSES.bend],
			[815, POSES.bend], [848, POSES.lift], [875, POSES.bend],
			[905, POSES.bend], [950, POSES.lift], [990, POSES.lift], [1050, POSES.hold],
		];
		const pose = poseAt(f, tl);
		pose.fa += dustWave;
		// lift height while bending: hip rises/falls with pose
		const bendDrop = kf(f, [700, 725, 755, 790, 815, 848, 875, 905, 950, 1050], [0, 17, 3, 17, 17, 3, 17, 17, 5, 0]);
		man = {x, y: y + bendDrop, rot, dir, pose, smile: kf(f, [1090, 1120], [-0.4, 1])};
	}

	// ---- kid ----
	let kid: null | {x: number; dir: number; pose: ReturnType<typeof poseAt>; smile: number} = null;
	if (f >= 860 && f < 1215) {
		if (f < 935) kid = {x: kf(f, [860, 935], [-90, 418], Easing.linear), dir: 1, pose: walkPose(f * 0.35), smile: 0};
		else if (f < 1135) {
			const pose = poseAt(f, [[935, POSES.stand], [955, POSES.bend], [990, POSES.lift], [1050, POSES.lift], [1080, POSES.stand], [1100, POSES.wave], [1125, POSES.wave], [1135, POSES.stand]]);
			if (f > 1100 && f < 1125) pose.fa += Math.sin(f * 0.6) * 18;
			kid = {x: kf(f, [990, 1050], [418, 440]), dir: 1, pose, smile: kf(f, [1060, 1090], [0.3, 1])};
		} else kid = {x: kf(f, [1135, 1215], [440, -150], Easing.linear), dir: -1, pose: walkPose(f * 0.35), smile: 1};
	}

	// ---- camera ----
	const zoom = kf(f, [0, 150, 200, 330, 345, 420, 700, 880, 935, 960, 1000, 1060, 1110, 1200], [1.0, 1.06, 1.25, 1.25, 1.4, 1.45, 1.6, 1.55, 1.75, 2.15, 2.15, 1.6, 1.35, 1.3]);
	let cx = f < 330 ? kf(f, [0, 150, 200], [540, 540, Math.max(BIKE_X(200), 0)]) : 0;
	if (f >= 200 && f < 330) cx = bx;
	if (f >= 330) cx = kf(f, [330, 360, 700, 935, 960, 1000, 1060, 1200], [bx, 680, 720, 680, 560, 580, 640, 640]);
	const cy = kf(f, [0, 150, 200, 935, 960, 1000, 1060, 1200], [960, 1000, 1210, 1230, 1220, 1215, 1200, 1150]);
	const halfW = 540 / zoom;
	const halfH = 960 / zoom;
	const ccx = Math.min(Math.max(cx, halfW), 1080 - halfW);
	const ccy = Math.min(Math.max(cy, halfH), 1920 - halfH);
	const shake = f >= 336 && f < 362 ? (1 - (f - 336) / 26) * 14 : 0;
	const sx = Math.sin(f * 2.1) * shake;
	const syy = Math.cos(f * 2.7) * shake;

	// ---- mood ----
	const warmth = kf(f, [990, 1110], [0, 1]);
	const rainAmt = kf(f, [0, 990, 1110], [1, 1, 0.3]);

	// splash particles at the fall
	const splash = f >= 340 && f < 385 ? new Array(16).fill(0).map((_, i) => {
		const t = (f - 340) / 45;
		const a = -Math.PI * (0.15 + 0.7 * random('sa' + i));
		const sp = 120 + random('ss' + i) * 160;
		return {x: 600 + Math.cos(a) * sp * t * (i % 2 ? 1 : -1), y: GY - 10 + Math.sin(a) * sp * t + 260 * t * t, o: 1 - t};
	}) : [];

	return (
		<AbsoluteFill style={{background: '#6f7d90'}}>
			<svg width={1080} height={1920} viewBox="0 0 1080 1920" style={{position: 'absolute'}}>
				<g transform={`translate(${540 + sx},${960 + syy}) scale(${zoom}) translate(${-ccx},${-ccy})`}>
					<City />
					<Pedestrians />
					<Traffic lane="far" />
					<Traffic lane="mid" />
					{/* shadow under bike */}
					<ellipse cx={bx} cy={GY + 4} rx={150} ry={10} fill="#000" opacity={0.25} />
					{kid && <Person x={kid.x} y={GY - 150 * 0.62 + (kid.pose === POSES.bend ? 0 : 0)} s={0.62} dir={kid.dir} pose={kid.pose} look="kid" smile={kid.smile} />}
					<Bike x={bx} y={GY + bump} sy={sy} rot={bikeRot} wr={wheelRot} />
					<Person x={man.x} y={man.y} dir={man.dir} rot={man.rot} pose={man.pose} look="man" smile={man.smile} />
					{splash.map((p, i) => <circle key={i} cx={p.x} cy={p.y} r={5} fill="#c9d6e6" opacity={p.o * 0.8} />)}
				</g>
			</svg>
			<Rain intensity={rainAmt} />
			{/* cold grade fading into warm light */}
			<AbsoluteFill style={{background: 'linear-gradient(180deg, rgba(70,90,120,0.25), rgba(40,50,70,0.15))', opacity: 1 - warmth}} />
			<AbsoluteFill style={{background: 'radial-gradient(circle at 80% 15%, rgba(255,200,130,0.55), rgba(255,170,100,0.12) 55%, rgba(0,0,0,0) 80%)', mixBlendMode: 'soft-light', opacity: warmth}} />
			<AbsoluteFill style={{background: 'radial-gradient(circle at 80% 12%, rgba(255,214,150,0.35), rgba(255,214,150,0) 50%)', opacity: warmth}} />
			<AbsoluteFill style={{background: 'radial-gradient(ellipse at center, rgba(0,0,0,0) 55%, rgba(0,0,0,0.45) 100%)'}} />
		</AbsoluteFill>
	);
};

// ================= flashback: a boy helping an old woman =================
const Flashback: React.FC = () => {
	const f = useCurrentFrame();
	const g = 1400;
	const oranges = useMemo(() => new Array(9).fill(0).map((_, i) => ({x: 300 + random('ox' + i) * 520, y: g - 12 + random('oy' + i) * 30})), []);
	const basket = {x: 640, y: g - 40};
	const boyX = kf(f, [0, 50], [-120, 470], Easing.out(Easing.quad));
	const boyPose = f < 50 ? walkPose(f * 0.45) : poseAt(f, [[50, POSES.stand], [65, POSES.bend], [200, POSES.bend], [215, POSES.stand]]);
	if (f > 65 && f < 200) boyPose.ua += Math.sin(f * 0.25) * 25;
	const oldPose = poseAt(f, [[0, P({t: 35, ua: 30, fa: 10, head: 10})], [200, P({t: 30, ua: 30, fa: 10, head: 10})], [215, P({t: 22, ua: 75, fa: 95, head: 5})]]);
	const o = kf(f, [0, 20, 235, 260], [0, 1, 1, 0]);
	const zoom = kf(f, [0, 260], [1.35, 1.5], Easing.linear);
	return (
		<AbsoluteFill style={{opacity: o, background: '#e9cf9e'}}>
			<AbsoluteFill style={{filter: 'sepia(0.55) saturate(0.85) contrast(0.95)'}}>
				<svg width={1080} height={1920} viewBox="0 0 1080 1920">
					<g transform={`translate(540,960) scale(${zoom}) translate(-560,-1150)`}>
						<rect x={-200} y={0} width={1500} height={1500} fill="#f3d9a6" />
						{[[-100, 260, '#d98f5a'], [200, 220, '#c9b48a'], [460, 280, '#b9765a'], [780, 240, '#d6b77c']].map(([x, h, c], i) => (
							<g key={i}>
								<rect x={x as number} y={g - 120 - (h as number)} width={250} height={h as number} fill={c as string} />
								<path d={`M ${(x as number) - 20} ${g - 120 - (h as number)} L ${(x as number) + 125} ${g - 200 - (h as number)} L ${(x as number) + 270} ${g - 120 - (h as number)} Z`} fill="#9a4a30" />
								<rect x={(x as number) + 90} y={g - 230} width={70} height={110} fill="#6b4a32" />
							</g>
						))}
						<rect x={-200} y={g - 120} width={1500} height={600} fill="#cda574" />
						<circle cx={900} cy={760} r={90} fill="#fff1c9" opacity={0.8} />
						<path d={`M ${basket.x - 60} ${basket.y} L ${basket.x + 60} ${basket.y} L ${basket.x + 45} ${basket.y + 45} L ${basket.x - 45} ${basket.y + 45} Z`} fill="#8a6a3a" />
						{oranges.map((p, i) => {
							const t0 = 70 + i * 14;
							const k = kf(f, [t0, t0 + 14], [0, 1]);
							const x = p.x + (basket.x - 30 + (i % 4) * 20 - p.x) * k;
							const y = p.y + (basket.y - 5 - p.y) * k - Math.sin(k * Math.PI) * 80;
							return <circle key={i} cx={x} cy={y} r={14} fill="#f08a24" />;
						})}
						<Person x={760} y={g - 150} s={0.95} dir={-1} pose={oldPose} look="old" smile={kf(f, [180, 210], [0, 1])} />
						<Person x={boyX} y={g - 150 * 0.6} s={0.6} dir={1} pose={boyPose} look="boy" smile={1} />
					</g>
				</svg>
			</AbsoluteFill>
			<AbsoluteFill style={{background: 'radial-gradient(ellipse at center, rgba(255,240,215,0) 45%, rgba(255,236,205,0.9) 100%)'}} />
		</AbsoluteFill>
	);
};

// ================= ripples: one small push travels =================
const Ripples: React.FC = () => {
	const f = useCurrentFrame();
	const gold = kf(f, [20, 150], [0, 1]);
	const rings = [];
	for (let i = 0; i < 9; i++) {
		const start = 8 + i * 16;
		const t = f - start;
		if (t < 0) continue;
		const r = t * 7;
		rings.push(<circle key={'m' + i} cx={540} cy={1000} r={r} fill="none" stroke={`rgb(${200 + 55 * gold},${215 - 15 * gold},${235 - 115 * gold})`} strokeWidth={4 - Math.min(3, t / 60)} opacity={Math.max(0, 0.9 - t / 160)} />);
	}
	for (let i = 0; i < 16; i++) {
		const start = random('rt' + i) * 170;
		const t = f - start;
		if (t < 0 || t > 50) continue;
		rings.push(<circle key={'s' + i} cx={random('rx' + i) * 1080} cy={random('ry' + i) * 1920} r={t * 2.2} fill="none" stroke="#cfd9e6" strokeWidth={2} opacity={(1 - t / 50) * 0.5} />);
	}
	const o = kf(f, [0, 15, 185, 200], [0, 1, 1, 0]);
	return (
		<AbsoluteFill style={{opacity: o, background: `linear-gradient(180deg, #24303f, #33404f ${60 - gold * 20}%, rgb(${60 + 90 * gold},${70 + 50 * gold},${80 + 10 * gold}))`}}>
			<AbsoluteFill style={{background: `radial-gradient(circle at 50% 52%, rgba(255,205,140,${0.35 * gold}), rgba(0,0,0,0) 60%)`}} />
			<svg width={1080} height={1920}>{rings}</svg>
		</AbsoluteFill>
	);
};

// ================= takeaway card =================
const EndCard: React.FC = () => {
	const f = useCurrentFrame();
	const a = kf(f, [0, 20], [0, 1]);
	const b = kf(f, [18, 42], [0, 1]);
	const c = kf(f, [50, 75], [0, 1]);
	return (
		<AbsoluteFill style={{opacity: a, background: 'linear-gradient(180deg, #f7ecdc, #f1d3ae)', alignItems: 'center', justifyContent: 'center', fontFamily: 'Georgia, "DejaVu Serif", serif'}}>
			<div style={{position: 'absolute', top: 640, left: 90, right: 90, textAlign: 'center'}}>
				<div style={{opacity: b, fontSize: 34, letterSpacing: 10, color: '#b0603a', fontFamily: 'sans-serif', fontWeight: 600}}>ONE SMALL THING</div>
				<div style={{opacity: b, width: 120, height: 3, background: '#d99a6c', margin: '34px auto'}} />
				<div style={{opacity: c, fontSize: 72, lineHeight: 1.28, color: '#3a2a20'}}>Today, stop for someone the city walks past.</div>
			</div>
			<svg width={1080} height={1920} style={{position: 'absolute', opacity: c}}>
				<Person x={540} y={1480 - 150 * 0.5} s={0.5} dir={1} pose={f > 80 ? {...POSES.wave, fa: POSES.wave.fa + Math.sin(f * 0.5) * 18} : POSES.stand} look="kid" smile={1} />
			</svg>
		</AbsoluteFill>
	);
};

// ================= full story =================
export const Story: React.FC = () => {
	const f = useCurrentFrame();
	const flash = kf(f, [1185, 1205, 1225], [0, 0.9, 0]);
	return (
		<AbsoluteFill style={{background: '#111'}}>
			<Sequence durationInFrames={1215}><CityScene /></Sequence>
			<Sequence from={1200} durationInFrames={260}><Flashback /></Sequence>
			<Sequence from={1445} durationInFrames={200}><Ripples /></Sequence>
			<Sequence from={1625} durationInFrames={175}><EndCard /></Sequence>
			<AbsoluteFill style={{background: '#fff6e6', opacity: flash}} />

			<Caption text="A rainy Monday morning in Chennai." from={20} to={140} />
			<Caption text="His bike was always a little too heavy for him." from={165} to={315} />
			<Caption text="He wasn't hurt." from={470} to={580} />
			<Caption text="But the whole city saw… and kept moving." from={590} to={700} />
			<Caption text="Once." from={728} to={788} size={74} />
			<Caption text="Twice." from={815} to={876} size={74} />
			<Caption text="“Come on anna, unga naala mudiyum!”" sub="(Come on, brother. You can do it.)" from={958} to={1092} italic color="#ffe08a" size={64} />
			<Caption text="It was just a kid. Maybe eight years old." from={1100} to={1192} />
			<Caption text="He remembered a boy who used to stop for strangers." from={1235} to={1440} color="#4a3220" />
			<Caption text="All day, he kept thinking about it." from={1455} to={1540} y={420} />
			<Caption text="One small push can travel further than you think." from={1545} to={1628} y={420} />
		</AbsoluteFill>
	);
};
