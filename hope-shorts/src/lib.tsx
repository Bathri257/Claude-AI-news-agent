import React, {useMemo} from 'react';
import {Easing, interpolate, random, useCurrentFrame} from 'remotion';

// ---------- timing helpers ----------
export const ease = Easing.inOut(Easing.cubic);
export const kf = (f: number, frames: number[], values: number[], easing = ease) =>
	interpolate(f, frames, values, {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing});

// ---------- poses (angles in degrees, measured from "straight down", positive = forward) ----------
export type Pose = {
	t: number; // torso lean
	ua: number; fa: number; // near upper arm / forearm
	ua2: number; fa2: number; // far arm
	th: number; sh: number; // near thigh / shin
	th2: number; sh2: number; // far leg
	head: number; // head tilt
};
export const P = (o: Partial<Pose> = {}): Pose => ({
	t: 0, ua: 4, fa: 2, ua2: -4, fa2: -2, th: 3, sh: 0, th2: -3, sh2: -2, head: 0, ...o,
});
export const lerpPose = (a: Pose, b: Pose, k: number): Pose => {
	const out = {} as Pose;
	(Object.keys(a) as (keyof Pose)[]).forEach((key) => {
		out[key] = a[key] + (b[key] - a[key]) * k;
	});
	return out;
};
// timeline of [frame, pose]
export const poseAt = (f: number, tl: [number, Pose][]): Pose => {
	if (f <= tl[0][0]) return tl[0][1];
	for (let i = 0; i < tl.length - 1; i++) {
		const [f0, p0] = tl[i];
		const [f1, p1] = tl[i + 1];
		if (f <= f1) return lerpPose(p0, p1, ease(Math.min(1, (f - f0) / Math.max(1, f1 - f0))));
	}
	return tl[tl.length - 1][1];
};

export const POSES = {
	stand: P(),
	ride: P({t: 30, ua: -9, fa: 92, ua2: -5, fa2: 95, th: 71, sh: -29, th2: 68, sh2: -26}),
	sit: P({t: -15, ua: -35, fa: -30, ua2: -40, fa2: -35, th: 120, sh: 10, th2: 115, sh2: 5, head: -5}),
	bend: P({t: 65, ua: 40, fa: 20, ua2: 35, fa2: 15, th: 35, sh: -15, th2: 30, sh2: -18, head: 10}),
	lift: P({t: 25, ua: 35, fa: 50, ua2: 30, fa2: 45, th: 15, sh: -5, th2: 10, sh2: -8, head: -5}),
	hold: P({t: 5, ua: 30, fa: 60, ua2: 25, fa2: 55}),
	dust: P({t: 15, ua: 25, fa: -40, ua2: 20, fa2: -30, head: 15}),
	sad: P({t: 8, head: 18}),
	wave: P({ua: 160, fa: 175, ua2: -5, fa2: -5, head: -8}),
	umbrella: P({ua: 60, fa: 170, ua2: -6, fa2: -4}),
};
export const walkPose = (phase: number, base: Partial<Pose> = {}) => {
	const s = Math.sin(phase);
	return P({th: 25 * s, sh: 25 * s - 12 * Math.max(0, -s) - 6, th2: -25 * s, sh2: -25 * s - 12 * Math.max(0, s) - 6, ua: -20 * s, fa: -10 * s + 10, ua2: 20 * s, fa2: 10 * s + 10, t: 4, ...base});
};

const rad = (a: number) => (a * Math.PI) / 180;
const vec = (a: number, L: number): [number, number] => [L * Math.sin(rad(a)), L * Math.cos(rad(a))];

// ---------- a person ----------
export type Look = 'man' | 'kid' | 'boy' | 'old' | 'ped';
export const Person: React.FC<{
	x: number; y: number; s?: number; dir?: number; rot?: number; pose: Pose; look: Look; smile?: number; opacity?: number; umbrella?: boolean; tint?: string;
}> = ({x, y, s = 1, dir = 1, rot = 0, pose, look, smile = 0, opacity = 1, umbrella, tint}) => {
	const L = {torso: 118, thigh: 75, shin: 75, ua: 58, fa: 55, neck: 34, head: 27};
	const hip: [number, number] = [0, 0];
	const sh: [number, number] = [L.torso * Math.sin(rad(pose.t)), -L.torso * Math.cos(rad(pose.t))];
	const add = (p: [number, number], q: [number, number]): [number, number] => [p[0] + q[0], p[1] + q[1]];
	const head = add(sh, [L.neck * Math.sin(rad(pose.t + pose.head * 0.3)), -L.neck * Math.cos(rad(pose.t))]);
	const limb = (base: [number, number], a1: number, l1: number, a2: number, l2: number) => {
		const m = add(base, vec(a1, l1));
		return [base, m, add(m, vec(a2, l2))] as [number, number][];
	};
	const armN = limb(sh, pose.ua, L.ua, pose.fa, L.fa);
	const armF = limb(sh, pose.ua2, L.ua, pose.fa2, L.fa);
	const legN = limb(hip, pose.th, L.thigh, pose.sh, L.shin);
	const legF = limb(hip, pose.th2, L.thigh, pose.sh2, L.shin);

	const C = {
		man: {skin: '#b97d55', top: '#8fb3d6', topDark: '#7699bd', pants: '#2e3440', hair: '#1d1a18', shoe: '#2a221c'},
		kid: {skin: '#a8714b', top: '#f2c230', topDark: '#d9a81f', pants: '#24345c', hair: '#1d1a18', shoe: '#3b2a20'},
		boy: {skin: '#b47a52', top: '#8fb3d6', topDark: '#7699bd', pants: '#5a4634', hair: '#1d1a18', shoe: '#3b2a20'},
		old: {skin: '#a2704d', top: '#8a2f3a', topDark: '#6e2430', pants: '#8a2f3a', hair: '#cfc8c0', shoe: '#4a3a2c'},
		ped: {skin: '#8d6a55', top: tint ?? '#4d5562', topDark: '#3d444f', pants: '#2b3038', hair: '#1d1a18', shoe: '#1f1f22'},
	}[look];
	const thick = look === 'man' ? 1 : look === 'ped' ? 1.1 : 1.05;
	const path = (pts: [number, number][]) => `M ${pts[0][0]} ${pts[0][1]} L ${pts[1][0]} ${pts[1][1]} L ${pts[2][0]} ${pts[2][1]}`;
	const Limb = ({pts, color, w}: {pts: [number, number][]; color: string; w: number}) => (
		<path d={path(pts)} stroke={color} strokeWidth={w * thick} strokeLinecap="round" strokeLinejoin="round" fill="none" />
	);
	const Foot = ({p}: {p: [number, number]}) => <ellipse cx={p[0] + 7} cy={p[1] + 2} rx={14} ry={7} fill={C.shoe} />;
	const Hand = ({p}: {p: [number, number]}) => <circle cx={p[0]} cy={p[1]} r={8} fill={C.skin} />;

	return (
		<g transform={`translate(${x},${y}) scale(${dir * s},${s}) rotate(${rot})`} opacity={opacity}>
			{/* school bag behind the kid */}
			{look === 'kid' && <rect x={sh[0] - 48} y={sh[1] + 8} width={30} height={62} rx={8} fill="#c7542f" transform={`rotate(${pose.t} ${sh[0]} ${sh[1]})`} />}
			<Limb pts={legF} color={C.pants} w={19} />
			<Foot p={legF[2]} />
			<Limb pts={armF} color={C.topDark} w={16} />
			<Hand p={armF[2]} />
			{/* torso */}
			{look === 'old' ? (
				<path d={`M ${sh[0] - 22} ${sh[1]} L ${sh[0] + 22} ${sh[1]} L 50 150 L -50 150 Z`} fill={C.top} />
			) : look === 'kid' ? (
				<path d={`M ${sh[0] - 20} ${sh[1] - 4} L ${sh[0] + 20} ${sh[1] - 4} L ${32} ${28} L ${-32} ${28} Z`} fill={C.top} />
			) : (
				<line x1={0} y1={0} x2={sh[0]} y2={sh[1]} stroke={C.top} strokeWidth={40 * thick} strokeLinecap="round" />
			)}
			{look !== 'old' && <Limb pts={legN} color={C.pants} w={19} />}
			{look !== 'old' && <Foot p={legN[2]} />}
			{look === 'old' && <Foot p={[legN[2][0], 150]} />}
			{/* head */}
			<g transform={`rotate(${pose.head} ${head[0]} ${head[1]})`}>
				<circle cx={head[0]} cy={head[1]} r={L.head} fill={C.skin} />
				{look === 'man' && (
					<>
						<path d={`M ${head[0] - 33} ${head[1] + 4} A 33 33 0 0 1 ${head[0] + 31} ${head[1] - 4} L ${head[0] + 10} ${head[1] - 2} L ${head[0] - 33} ${head[1] + 6} Z`} fill="#c23b32" />
						<path d={`M ${head[0] + 31} ${head[1] - 4} L ${head[0] + 10} ${head[1] - 2}`} stroke="#3a3f46" strokeWidth={5} />
					</>
				)}
				{(look === 'boy' || look === 'ped') && <path d={`M ${head[0] - 27} ${head[1]} A 27 27 0 0 1 ${head[0] + 26} ${head[1] - 8} Q ${head[0]} ${head[1] - 16} ${head[0] - 27} ${head[1]} Z`} fill={C.hair} />}
				{look === 'kid' && <path d={`M ${head[0] - 33} ${head[1] + 12} A 33 33 0 1 1 ${head[0] + 30} ${head[1] - 12} Q ${head[0] + 5} ${head[1] - 22} ${head[0] - 18} ${head[1] + 14} Z`} fill={C.top} />}
				{look === 'old' && <><circle cx={head[0] - 22} cy={head[1] - 8} r={12} fill={C.hair} /><path d={`M ${head[0] - 27} ${head[1]} A 27 27 0 0 1 ${head[0] + 26} ${head[1] - 8} Q ${head[0]} ${head[1] - 14} ${head[0] - 27} ${head[1]} Z`} fill={C.hair} /></>}
				{/* face */}
				<circle cx={head[0] + 13} cy={head[1] + 2} r={3.2} fill="#1b1512" />
				<path d={`M ${head[0] + 9} ${head[1] + 14} Q ${head[0] + 15} ${head[1] + 14 + 6 * smile} ${head[0] + 21} ${head[1] + 13}`} stroke="#4a2a1e" strokeWidth={2.6} fill="none" strokeLinecap="round" />
			</g>
			<Limb pts={armN} color={C.top} w={17} />
			<Hand p={armN[2]} />
			{umbrella && (
				<g transform={`translate(${armN[2][0]},${armN[2][1]})`}>
					<line x1={0} y1={0} x2={0} y2={-120} stroke="#222" strokeWidth={4} />
					<path d="M -95 -110 Q 0 -190 95 -110 Q 70 -122 48 -110 Q 24 -124 0 -110 Q -24 -124 -48 -110 Q -70 -122 -95 -110 Z" fill="#23262d" />
				</g>
			)}
		</g>
	);
};

// ---------- bike (generic red commuter bike, no branding) ----------
const Wheel: React.FC<{cx: number; cy: number; r: number; rot: number}> = ({cx, cy, r, rot}) => (
	<g transform={`translate(${cx},${cy}) rotate(${rot})`}>
		<circle r={r} fill="none" stroke="#16161a" strokeWidth={17} />
		<circle r={r - 11} fill="none" stroke="#a3a8ae" strokeWidth={4} />
		{[0, 30, 60, 90, 120, 150].map((a) => (
			<line key={a} x1={-(r - 12) * Math.cos(rad(a))} y1={-(r - 12) * Math.sin(rad(a))} x2={(r - 12) * Math.cos(rad(a))} y2={(r - 12) * Math.sin(rad(a))} stroke="#8d9298" strokeWidth={2} />
		))}
		<circle r={11} fill="#5b6067" />
	</g>
);
export const Bike: React.FC<{x: number; y: number; sy?: number; rot?: number; wr?: number}> = ({x, y, sy = 1, rot = 0, wr = 0}) => (
	<g transform={`translate(${x},${y}) rotate(${rot}) scale(1,${sy})`}>
		<Wheel cx={-115} cy={-68} r={66} rot={wr} />
		<Wheel cx={118} cy={-68} r={66} rot={wr} />
		<line x1={-115} y1={-68} x2={-20} y2={-110} stroke="#2a2a2e" strokeWidth={12} />
		<line x1={118} y1={-68} x2={88} y2={-200} stroke="#9aa0a8" strokeWidth={10} />
		<path d="M -20 -110 L 75 -175 L 88 -200" stroke="#2a2a2e" strokeWidth={14} fill="none" />
		<rect x={-35} y={-135} width={75} height={55} rx={10} fill="#3d3f45" />
		<path d="M 20 -85 L -100 -95 L -150 -100" stroke="#b8bcc2" strokeWidth={10} strokeLinecap="round" fill="none" />
		<path d="M 0 -180 Q 40 -215 85 -195 L 70 -160 L 5 -160 Z" fill="#b3262e" />
		<path d="M -140 -165 L -60 -168 L -40 -140 L -110 -140 Z" fill="#b3262e" />
		<path d="M -110 -175 L 5 -178 L 5 -165 L -100 -160 Z" fill="#1b1b1d" />
		<path d="M 70 -125 Q 118 -150 170 -120" stroke="#b3262e" strokeWidth={9} fill="none" />
		<ellipse cx={108} cy={-200} rx={14} ry={18} fill="#e9e4c8" />
		<line x1={88} y1={-200} x2={60} y2={-232} stroke="#2a2a2e" strokeWidth={8} strokeLinecap="round" />
	</g>
);

// ---------- vehicles ----------
export const Car: React.FC<{x: number; y: number; s: number; dir: number; color: string; kind: number}> = ({x, y, s, dir, color, kind}) => {
	if (kind === 2) {
		// city bus
		return (
			<g transform={`translate(${x},${y}) scale(${dir * s},${s})`}>
				<rect x={-270} y={-230} width={540} height={195} rx={20} fill={color} />
				<rect x={-270} y={-95} width={540} height={22} fill="#e8e2d0" opacity={0.8} />
				{[-240, -165, -90, -15, 60, 135].map((wx) => <rect key={wx} x={wx} y={-210} width={62} height={70} rx={6} fill="#a9bccd" opacity={0.75} />)}
				<rect x={212} y={-210} width={50} height={110} rx={6} fill="#a9bccd" opacity={0.8} />
				<circle cx={-170} cy={-35} r={32} fill="#18181b" /><circle cx={170} cy={-35} r={32} fill="#18181b" />
				<ellipse cx={330} cy={-70} rx={70} ry={14} fill="#fff3c4" opacity={0.18} />
			</g>
		);
	}
	if (kind === 1) {
		// auto rickshaw
		return (
			<g transform={`translate(${x},${y}) scale(${dir * s},${s})`}>
				<path d="M -95 -40 L -95 -150 Q -60 -205 40 -200 Q 90 -195 95 -120 L 95 -40 Z" fill="#20252b" />
				<path d="M -100 -150 Q -60 -215 40 -208 Q 95 -203 100 -150 Z" fill="#f2c230" />
				<path d="M 40 -150 L 92 -150 L 92 -60 L 40 -60 Z" fill="#9fb3c8" opacity={0.5} />
				<rect x={-95} y={-75} width={190} height={35} fill="#2d7a4a" />
				<circle cx={-60} cy={-30} r={22} fill="#18181b" /><circle cx={75} cy={-30} r={22} fill="#18181b" />
			</g>
		);
	}
	return (
		<g transform={`translate(${x},${y}) scale(${dir * s},${s})`}>
			<rect x={-130} y={-95} width={260} height={60} rx={22} fill={color} />
			<path d="M -70 -93 L -40 -145 L 55 -145 L 92 -93 Z" fill={color} />
			<path d="M -58 -98 L -35 -137 L 5 -137 L 5 -98 Z" fill="#9fb3c8" opacity={0.7} />
			<path d="M 12 -98 L 12 -137 L 50 -137 L 78 -98 Z" fill="#9fb3c8" opacity={0.7} />
			<circle cx={-80} cy={-35} r={27} fill="#18181b" /><circle cx={80} cy={-35} r={27} fill="#18181b" />
			<circle cx={-80} cy={-35} r={10} fill="#777" /><circle cx={80} cy={-35} r={10} fill="#777" />
			<rect x={118} y={-82} width={12} height={13} rx={3} fill="#fff5c0" />
			<ellipse cx={200} cy={-74} rx={80} ry={14} fill="#fff3c4" opacity={0.2} />
			<rect x={-133} y={-84} width={8} height={14} rx={3} fill="#ff4d4d" />
		</g>
	);
};

// ---------- rain (screen space) ----------
export const Rain: React.FC<{intensity: number; count?: number}> = ({intensity, count = 240}) => {
	const f = useCurrentFrame();
	const drops = useMemo(
		() => new Array(count).fill(0).map((_, i) => ({x: random('rx' + i) * 1400 - 60, s: random('rs' + i) * 22 + 40, l: random('rl' + i) * 45 + 30, o: random('ro' + i) * 0.35 + 0.15, ph: random('rp' + i) * 2100})),
		[count],
	);
	return (
		<svg width={1080} height={1920} style={{position: 'absolute', inset: 0}}>
			{drops.map((d, i) => {
				if (i / drops.length > intensity) return null;
				const y = ((d.ph + f * d.s) % 2100) - 100;
				const x = d.x - y * 0.13;
				return <line key={i} x1={x} y1={y} x2={x - d.l * 0.13} y2={y + d.l} stroke="#dbe5f0" strokeOpacity={d.o} strokeWidth={2.2} strokeLinecap="round" />;
			})}
		</svg>
	);
};

// ---------- captions ----------
export const Caption: React.FC<{text: string; from: number; to: number; y?: number; size?: number; italic?: boolean; color?: string; sub?: string}> = ({text, from, to, y = 330, size = 62, italic, color = '#fbf6ee', sub}) => {
	const f = useCurrentFrame();
	if (f < from - 1 || f > to + 1) return null;
	const o = kf(f, [from, from + 14, to - 14, to], [0, 1, 1, 0]);
	const dy = kf(f, [from, from + 20], [18, 0]);
	return (
		<div style={{position: 'absolute', left: 70, right: 70, top: y + dy, textAlign: 'center', opacity: o, fontFamily: 'Georgia, "DejaVu Serif", serif'}}>
			<div style={{fontSize: size, lineHeight: 1.25, color, fontStyle: italic ? 'italic' : 'normal', textShadow: '0 3px 18px rgba(0,0,0,0.55), 0 1px 3px rgba(0,0,0,0.6)'}}>{text}</div>
			{sub && <div style={{marginTop: 18, fontSize: size * 0.6, color: '#e6e0d6', textShadow: '0 2px 10px rgba(0,0,0,0.6)'}}>{sub}</div>}
		</div>
	);
};
