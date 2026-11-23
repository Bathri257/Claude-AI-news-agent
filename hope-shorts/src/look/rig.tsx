// Poseable illustrated characters.  Units: 400 units = 1 metre (1 unit = 2.5 mm).
// Characters face right (+x).  Angles are in degrees measured from "straight down", positive = forward (+x).
import React from 'react';

export type V = [number, number];
const R = Math.PI / 180;
export const add = (a: V, b: V): V => [a[0] + b[0], a[1] + b[1]];
export const dirv = (ang: number, len: number): V => [len * Math.sin(ang * R), len * Math.cos(ang * R)];
export const angOf = (v: V) => Math.atan2(v[0], v[1]) / R;

// 2-bone IK: returns [upperAngle, lowerAngle]. bend = +1 bends the joint forward (knees), -1 backward (elbows)
export const ik = (base: V, target: V, l1: number, l2: number, bend: 1 | -1): [number, number] => {
	const dx = target[0] - base[0];
	const dy = target[1] - base[1];
	let d = Math.hypot(dx, dy);
	d = Math.min(Math.max(d, Math.abs(l1 - l2) + 0.5), l1 + l2 - 0.5);
	const a = (l1 * l1 - l2 * l2 + d * d) / (2 * d);
	const h = Math.sqrt(Math.max(0, l1 * l1 - a * a));
	const ux = dx / Math.hypot(dx, dy);
	const uy = dy / Math.hypot(dx, dy);
	const px = -uy * bend;
	const py = ux * bend;
	const j: V = [base[0] + a * ux + h * px, base[1] + a * uy + h * py];
	return [angOf([j[0] - base[0], j[1] - base[1]]), angOf([target[0] - j[0], target[1] - j[1]])];
};

export type Pose = {
	t: number; neck: number; head: number;
	ua: number; fa: number; hand: number; // near arm
	ua2: number; fa2: number; hand2: number; // far arm
	th: number; sh: number; foot: number; // near leg
	th2: number; sh2: number; foot2: number; // far leg
};
export const pose = (o: Partial<Pose> = {}): Pose => ({
	t: 0, neck: 4, head: 0, ua: 6, fa: 14, hand: 0, ua2: -4, fa2: 8, hand2: 0, th: 4, sh: -2, foot: 0, th2: -5, sh2: -7, foot2: 0, ...o,
});
export type Face = {brow?: number; smile?: number; open?: number; look?: number; blink?: number};

// ---------------- shared pieces ----------------
const limbPath = (len: number, w0: number, w1: number, bulge = 0) =>
	`M ${-w0 / 2} 0 Q ${-w0 / 2 - bulge} ${len * 0.45} ${-w1 / 2} ${len} L ${w1 / 2} ${len} Q ${w0 / 2 + bulge} ${len * 0.45} ${w0 / 2} 0 Z`;

const Scar: React.FC<{y: number; s?: number}> = ({y, s = 1}) => (
	<g transform={`translate(${5 * s},${y}) rotate(-14) scale(${s})`}>
		<path d="M 0 0 Q 2 13 1 26" stroke="#e5b49c" strokeWidth={3.4} fill="none" strokeLinecap="round" opacity={0.95} />
		<path d="M 0 0 Q 2 13 1 26" stroke="#7a4632" strokeWidth={0.9} fill="none" strokeLinecap="round" opacity={0.6} transform="translate(1.6,0)" />
		{[5, 11, 17, 22].map((k) => <line key={k} x1={-3} y1={k} x2={5} y2={k + 1} stroke="#d9a28a" strokeWidth={1.4} strokeLinecap="round" />)}
	</g>
);

export const Defs: React.FC = () => (
	<defs>
		<pattern id="weave" width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(30)">
			<rect width="6" height="6" fill="none" />
			<line x1="0" y1="0" x2="0" y2="6" stroke="#ffffff" strokeOpacity="0.16" strokeWidth="1.4" />
			<line x1="0" y1="3" x2="6" y2="3" stroke="#28567a" strokeOpacity="0.12" strokeWidth="1" />
		</pattern>
		<filter id="soft" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="7" /></filter>
		<filter id="soft2" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="2.5" /></filter>
		<linearGradient id="lit" x1="0" y1="0" x2="1" y2="0">
			<stop offset="0" stopColor="#fff" stopOpacity="0.18" />
			<stop offset="0.45" stopColor="#fff" stopOpacity="0" />
			<stop offset="1" stopColor="#000" stopOpacity="0.22" />
		</linearGradient>
		<linearGradient id="litV" x1="0" y1="0" x2="0" y2="1">
			<stop offset="0" stopColor="#fff" stopOpacity="0.16" />
			<stop offset="1" stopColor="#000" stopOpacity="0.2" />
		</linearGradient>
	</defs>
);

const Drop: React.FC<{x: number; y: number; r?: number}> = ({x, y, r = 4}) => (
	<g>
		<ellipse cx={x} cy={y} rx={r} ry={r * 1.15} fill="#ffffff" fillOpacity={0.22} stroke="#2a2a2a" strokeOpacity={0.18} strokeWidth={0.8} />
		<circle cx={x - r * 0.35} cy={y - r * 0.4} r={r * 0.32} fill="#fff" fillOpacity={0.9} />
	</g>
);

// ---------------- the man ----------------
export type Outfit = {
	skin: string; skinShade: string; shirt: string; shirtShade: string; wet?: string; pants: string; pantsShade: string;
	shoes: string; belt?: string; helmet?: boolean; hair: string; kurta?: boolean; scar?: boolean; texture?: boolean; mustache?: boolean;
	umbrella?: string; bag?: string; mud?: boolean;
};
export const HERO: Outfit = {
	skin: '#9c6a48', skinShade: '#7c5034', shirt: '#8fc6e8', shirtShade: '#6aa4cc', wet: '#4f8dbb', pants: '#6e7279', pantsShade: '#55595f',
	shoes: '#5e3b22', belt: '#6a4227', helmet: true, hair: '#1c1512', scar: true, texture: true, mustache: true,
};

const L = {torso: 205, neck: 18, ua: 118, fa: 108, th: 172, sh: 168};

const ManHead: React.FC<{o: Outfit; face: Face}> = ({o, face}) => {
	const brow = face.brow ?? 0;
	const sm = face.smile ?? 0;
	const lk = face.look ?? 0;
	const blink = face.blink ?? 0;
	const eyeH = 5.2 * (1 - blink);
	return (
		<g>
			{/* ear */}
			<path d="M -8 -64 Q -26 -70 -27 -50 Q -27 -32 -10 -31 Z" fill={o.skin} />
			<path d="M -12 -58 Q -21 -58 -20 -48 Q -19 -40 -12 -39" stroke={o.skinShade} strokeWidth={2.4} fill="none" />
			{/* skull + face */}
			<path id="mface" d="M -28 -40 Q -34 -88 -4 -104 Q 28 -116 46 -90 Q 52 -76 50 -63 L 55 -47 Q 57 -42 51 -40 L 50 -31 Q 49 -25 46 -22 Q 44 -12 38 -6 Q 26 4 12 2 Q -6 0 -18 -10 Q -28 -20 -28 -40 Z" fill={o.skin} />
			<path d="M -28 -40 Q -34 -88 -4 -104 Q 28 -116 46 -90 Q 52 -76 50 -63 L 55 -47 Q 57 -42 51 -40 L 50 -31 Q 49 -25 46 -22 Q 44 -12 38 -6 Q 26 4 12 2 Q -6 0 -18 -10 Q -28 -20 -28 -40 Z" fill="url(#lit)" />
			{/* cheek / jaw shade */}
			<path d="M -18 -10 Q -6 -2 10 0 Q 26 2 38 -6 Q 30 -14 14 -16 Q -4 -18 -18 -10 Z" fill={o.skinShade} opacity={0.5} />
			{o.mustache && <path d="M -10 -32 Q 10 -26 30 -30 Q 44 -27 46 -21 Q 44 -10 37 -5 Q 25 4 11 2 Q -5 0 -15 -10 Z" fill="#2b1d16" opacity={0.2} />}
			{/* nose */}
			<path d="M 47 -60 Q 54 -48 55 -44 Q 53 -39 46 -40" stroke={o.skinShade} strokeWidth={2.6} fill="none" strokeLinecap="round" />
			<circle cx={47} cy={-41} r={1.8} fill="#3a2418" />
			{/* eyes */}
			<path d={`M 15 -55 Q 24 ${-61 + blink * 5} 33 -55 Q 24 ${-50 - blink * 1} 15 -55 Z`} fill="#efe8dd" />
			{blink < 0.8 && <circle cx={25.5 + lk * 4} cy={-55.5} r={eyeH * 0.72} fill="#2a1a11" />}
			{blink < 0.8 && <circle cx={24 + lk * 4} cy={-57} r={1.2} fill="#fff" />}
			<path d={`M 14 -55 Q 24 ${-62 + blink * 6} 34 -56`} stroke="#1d130d" strokeWidth={2.6} fill="none" strokeLinecap="round" />
			<path d="M 17 -51 Q 24 -49 31 -52" stroke={o.skinShade} strokeWidth={1.2} fill="none" opacity={0.7} />
			<path d={`M 42 -56 Q 46 ${-60 + blink * 4} 49 -56 Q 46 -53 42 -56 Z`} fill="#efe8dd" />
			{blink < 0.8 && <circle cx={46 + lk * 2} cy={-56} r={2.6} fill="#2a1a11" />}
			<path d={`M 41 -56 Q 46 ${-61 + blink * 5} 50 -57`} stroke="#1d130d" strokeWidth={2} fill="none" />
			{/* brows (brow>0 = worried) */}
			<path d={`M 13 ${-65 + brow * 1} Q 23 ${-70 - brow * 3} 34 ${-66 - brow * 5}`} stroke={o.hair} strokeWidth={4.4} fill="none" strokeLinecap="round" />
			<path d={`M 41 ${-67 - brow * 4} Q 46 ${-69 - brow * 2} 51 -66`} stroke={o.hair} strokeWidth={3.4} fill="none" strokeLinecap="round" />
			{/* mustache + mouth */}
			{o.mustache && <path d="M 33 -32 Q 42 -36 51 -32 Q 49 -27.5 42 -29 Q 37 -27.5 33 -32 Z" fill="#241712" />}
			<path d={`M 35 ${-22 + sm * 0.5} Q 42 ${-21 + sm * 4} 48 ${-23 - sm * 1.5}`} stroke="#4b261b" strokeWidth={2.4} fill="none" strokeLinecap="round" />
			{(face.open ?? 0) > 0 && <ellipse cx={42} cy={-20} rx={4} ry={3 * (face.open ?? 0)} fill="#3a1610" />}
			{/* hair under helmet */}
			<path d="M -5 -67 L 4 -67 L 1 -47 L -5 -50 Z" fill={o.hair} />
			<path d="M -27 -54 Q -33 -40 -24 -27 L -20 -42 Z" fill={o.hair} />
			{o.helmet ? (
				<g>
					<path d="M -33 -58 Q -40 -104 0 -117 Q 38 -126 53 -88 Q 55 -77 51 -71 Q 30 -76 10 -71 Q -12 -66 -33 -58 Z" fill="#1d1f25" />
					<path d="M 28 -74 Q 46 -77 62 -70 Q 53 -65 44 -67 Q 36 -69 28 -74 Z" fill="#14161a" />
					<path d="M -20 -102 Q 6 -118 34 -110" stroke="#6b7280" strokeWidth={5} fill="none" opacity={0.55} strokeLinecap="round" />
					<path d="M -31 -66 Q 10 -78 50 -76" stroke="#2f6fb3" strokeWidth={2.5} fill="none" opacity={0.85} />
					<path d="M -9 -62 Q -2 -30 16 -3" stroke="#0e0f12" strokeWidth={3} fill="none" />
					<Drop x={4} y={-108} r={3} /><Drop x={26} y={-104} r={2.4} /><Drop x={-16} y={-96} r={2.2} />
				</g>
			) : (
				<path d="M -30 -50 Q -36 -98 -2 -110 Q 34 -120 50 -86 Q 44 -92 30 -92 Q 12 -88 -2 -80 Q -10 -70 -12 -58 Q -20 -60 -30 -50 Z" fill={o.hair} />
			)}
		</g>
	);
};

const Hand: React.FC<{skin: string; shade: string; grip?: boolean; s?: number}> = ({skin, shade, grip, s = 1}) =>
	grip ? (
		<g transform={`scale(${s})`}>
			<path d="M -13 -2 Q -16 18 -10 34 Q 2 42 14 34 Q 18 16 13 -2 Z" fill={skin} />
			<path d="M -10 26 Q 2 31 13 26" stroke={shade} strokeWidth={1.6} fill="none" />
			<path d="M 10 6 Q 22 14 16 26" stroke={skin} strokeWidth={9} fill="none" strokeLinecap="round" />
		</g>
	) : (
		<g transform={`scale(${s})`}>
			<path d="M -12 -2 Q -15 20 -9 40 Q -4 50 4 50 Q 12 48 13 38 Q 16 18 12 -2 Z" fill={skin} />
			<path d="M 10 8 Q 22 20 16 32" stroke={skin} strokeWidth={8} fill="none" strokeLinecap="round" />
			<path d="M -4 32 L -3 46 M 3 34 L 4 48" stroke={shade} strokeWidth={1.3} opacity={0.7} />
		</g>
	);

export const Man: React.FC<{p: Pose; o?: Outfit; face?: Face; s?: number; dir?: 1 | -1; x?: number; y?: number}> = ({p, o = HERO, face = {}, s = 1, dir = 1, x = 0, y = 0}) => {
	const neckBase: V = add([0, 0], [L.torso * Math.sin(p.t * R), -L.torso * Math.cos(p.t * R)]);
	const shoulder: V = add(neckBase, [-6 * Math.cos(p.t * R), 22]);
	const shoulderF: V = add(shoulder, [-10, 2]);
	const elbow = add(shoulder, dirv(p.ua, L.ua));
	const wrist = add(elbow, dirv(p.fa, L.fa));
	const elbow2 = add(shoulderF, dirv(p.ua2, L.ua));
	const wrist2 = add(elbow2, dirv(p.fa2, L.fa));
	const hipN: V = [6, 4];
	const hipF: V = [-6, 2];
	const knee = add(hipN, dirv(p.th, L.th));
	const ankle = add(knee, dirv(p.sh, L.sh));
	const knee2 = add(hipF, dirv(p.th2, L.th));
	const ankle2 = add(knee2, dirv(p.sh2, L.sh));
	const rot = (a: number) => -a;

	const Thigh = ({c}: {c: string}) => (
		<g>
			<path d={limbPath(L.th + 6, 66, 46, 4)} fill={c} />
			<path d={limbPath(L.th + 6, 66, 46, 4)} fill="url(#lit)" />
			<path d={`M -8 ${L.th - 30} Q 2 ${L.th - 18} 14 ${L.th - 24}`} stroke="#000" strokeOpacity={0.18} strokeWidth={2} fill="none" />
		</g>
	);
	const Shin = ({c}: {c: string}) => (
		<g>
			<path d={`M -23 -4 L -21 ${L.sh - 6} Q -24 ${L.sh + 4} -22 ${L.sh + 8} L 24 ${L.sh + 8} Q 25 ${L.sh} 21 ${L.sh - 6} L 23 -4 Z`} fill={c} />
			<path d={`M -23 -4 L -21 ${L.sh - 6} Q -24 ${L.sh + 4} -22 ${L.sh + 8} L 24 ${L.sh + 8} Q 25 ${L.sh} 21 ${L.sh - 6} L 23 -4 Z`} fill="url(#lit)" />
			<path d={`M 2 10 L 3 ${L.sh}`} stroke="#000" strokeOpacity={0.1} strokeWidth={2} />
			{o.mud && <g opacity={0.75}><ellipse cx={6} cy={8} rx={18} ry={14} fill="#5b4632" filter="url(#soft2)" /><ellipse cx={-6} cy={40} rx={9} ry={6} fill="#5b4632" filter="url(#soft2)" /><circle cx={12} cy={64} r={4} fill="#5b4632" /></g>}
		</g>
	);
	const Shoe = ({c}: {c: string}) => (
		<g>
			<path d="M -22 -4 L 16 -6 Q 30 2 52 8 Q 68 13 67 24 L 67 28 L -25 28 Q -29 10 -22 -4 Z" fill={c} />
			<path d="M -25 24 L 67 24 L 67 29 L -25 29 Z" fill="#24170f" />
			<path d="M 20 0 Q 40 6 58 12" stroke="#fff" strokeOpacity={0.22} strokeWidth={3} fill="none" />
		</g>
	);
	const UpperArm = ({c, near}: {c: string; near: boolean}) => (
		<g>
			<path d={limbPath(L.ua - 8, 44, 38, 3)} fill={c} />
			{o.texture && <path d={limbPath(L.ua - 8, 44, 38, 3)} fill="url(#weave)" />}
			<path d={limbPath(L.ua - 8, 44, 38, 3)} fill="url(#lit)" />
			{near && o.wet && <ellipse cx={-6} cy={22} rx={14} ry={20} fill={o.wet} opacity={0.5} filter="url(#soft2)" />}
			{/* rolled cuff */}
			<rect x={-22} y={L.ua - 30} width={44} height={22} rx={8} fill={c} />
			<rect x={-22} y={L.ua - 30} width={44} height={22} rx={8} fill="url(#litV)" />
			<path d={`M -20 ${L.ua - 20} L 20 ${L.ua - 21}`} stroke={o.shirtShade} strokeWidth={2} />
		</g>
	);
	const Forearm = ({near}: {near: boolean}) => (
		<g>
			<path d={limbPath(L.fa, 32, 24, 3)} fill={o.skin} />
			<path d={limbPath(L.fa, 32, 24, 3)} fill="url(#lit)" />
			{near && o.scar && <Scar y={36} />}
		</g>
	);

	const torsoPath = `M -36 4 Q -42 -70 -42 -140 Q -40 -186 -24 -${L.torso} Q -6 -${L.torso + 8} 10 -${L.torso + 2} Q 34 -${L.torso - 14} 38 -168 Q 42 -128 36 -70 Q 34 -30 34 4 Z`;

	return (
		<g transform={`translate(${x},${y}) scale(${dir * s},${s})`}>
			{/* far arm */}
			<g style={{filter: "brightness(0.8)"}}>
				<g transform={`translate(${shoulderF[0]},${shoulderF[1]}) rotate(${rot(p.ua2)})`}><UpperArm c={o.shirtShade} near={false} /></g>
				<g transform={`translate(${elbow2[0]},${elbow2[1]}) rotate(${rot(p.fa2)})`}><Forearm near={false} /></g>
				<g transform={`translate(${wrist2[0]},${wrist2[1]}) rotate(${rot(p.fa2 + p.hand2)})`}><Hand skin={o.skinShade} shade="#5a3826" /></g>
			</g>
			{/* far leg */}
			<g transform={`translate(${hipF[0]},${hipF[1]}) rotate(${rot(p.th2)})`}><Thigh c={o.pantsShade} /></g>
			<g transform={`translate(${knee2[0]},${knee2[1]}) rotate(${rot(p.sh2)})`}><Shin c={o.pantsShade} /></g>
			<g transform={`translate(${ankle2[0]},${ankle2[1] + 6}) rotate(${p.foot2})`}><Shoe c="#4a2e1a" /></g>
			{/* pelvis */}
			<ellipse cx={0} cy={14} rx={38} ry={30} fill={o.pants} />
			{/* torso */}
			<g transform={`rotate(${p.t})`}>
				{o.bag && <path d={`M -44 -180 Q -86 -176 -84 -120 L -82 -60 Q -80 -40 -50 -42 Z`} fill={o.bag} />}
				<path d={torsoPath} fill={o.shirt} />
				{o.texture && <path d={torsoPath} fill="url(#weave)" />}
				<path d={torsoPath} fill="url(#lit)" />
				<clipPath id="torsoClip"><path d={torsoPath} /></clipPath>
				{o.wet && (
					<g opacity={0.55} clipPath="url(#torsoClip)">
						<ellipse cx={-20} cy={-185} rx={26} ry={18} fill={o.wet} filter="url(#soft)" />
						<ellipse cx={18} cy={-178} rx={18} ry={14} fill={o.wet} filter="url(#soft)" />
						<ellipse cx={-30} cy={-120} rx={12} ry={30} fill={o.wet} filter="url(#soft)" />
						<ellipse cx={22} cy={-95} rx={9} ry={12} fill={o.wet} filter="url(#soft)" opacity={0.7} />
					</g>
				)}
				{o.kurta ? (
					<path d="M -36 0 L -46 120 L 46 120 L 34 0 Z" fill={o.shirt} />
				) : (
					<g>
						{/* shirt blousing over belt */}
						<path d="M -36 -8 Q -10 -2 34 -8" stroke={o.shirtShade} strokeWidth={3} fill="none" />
						<path d="M -20 -40 Q -12 -22 -4 -10 M 10 -50 Q 16 -30 20 -12" stroke={o.shirtShade} strokeWidth={2} fill="none" opacity={0.7} />
						{/* placket + buttons */}
						<path d={`M 26 -${L.torso - 8} Q 34 -120 30 -6`} stroke={o.shirtShade} strokeWidth={2.2} fill="none" />
						{[-170, -130, -90, -50].map((by) => <circle key={by} cx={by < -150 ? 29 : by < -110 ? 33 : 32} cy={by} r={2.6} fill="#eef3f6" />)}
						{/* pocket */}
						<path d="M 2 -158 L 24 -160 L 25 -132 Q 14 -128 3 -131 Z" fill="none" stroke={o.shirtShade} strokeWidth={2} />
						{/* collar */}
						<path d={`M -22 -${L.torso - 2} Q -8 -${L.torso + 16} 20 -${L.torso + 6} L 32 -${L.torso - 24} L 10 -${L.torso - 12} Z`} fill={o.shirt} stroke={o.shirtShade} strokeWidth={2} />
						{/* belt */}
						{o.belt && (
							<g>
								<path d="M -37 -6 L 34 -8 L 35 8 L -37 10 Z" fill={o.belt} />
								<rect x={22} y={-9} width={14} height={17} rx={2} fill="none" stroke="#c8bea8" strokeWidth={3} />
								<line x1={-10} y1={-6} x2={-10} y2={9} stroke="#3b2416" strokeWidth={4} />
							</g>
						)}
					</g>
				)}
			</g>
			{/* near leg */}
			<g transform={`translate(${hipN[0]},${hipN[1]}) rotate(${rot(p.th)})`}><Thigh c={o.pants} /></g>
			<g transform={`translate(${knee[0]},${knee[1]}) rotate(${rot(p.sh)})`}><Shin c={o.pants} /></g>
			<g transform={`translate(${ankle[0]},${ankle[1] + 6}) rotate(${p.foot})`}><Shoe c={o.shoes} /></g>
			{/* neck + head */}
			<g transform={`translate(${neckBase[0]},${neckBase[1]}) rotate(${p.t + p.neck})`}>
				<path d={`M -14 6 L -12 -${L.neck} L 16 -${L.neck} L 18 6 Z`} fill={o.skinShade} />
				<g transform={`translate(4,-${L.neck - 4}) rotate(${p.head})`}><ManHead o={o} face={face} /></g>
			</g>
			{/* near arm */}
			<g transform={`translate(${shoulder[0]},${shoulder[1]}) rotate(${rot(p.ua)})`}><UpperArm c={o.shirt} near /></g>
			<g transform={`translate(${elbow[0]},${elbow[1]}) rotate(${rot(p.fa)})`}><Forearm near /></g>
			<g transform={`translate(${wrist[0]},${wrist[1]}) rotate(${rot(p.fa + p.hand)})`}><Hand skin={o.skin} shade={o.skinShade} /></g>
			{o.umbrella && (
				<g transform={`translate(${wrist[0]},${wrist[1] + 20})`}>
					<line x1={0} y1={0} x2={-4} y2={-330} stroke="#222" strokeWidth={5} />
					<path d="M -200 -300 Q -4 -440 196 -300 Q 150 -320 98 -298 Q 48 -322 -4 -298 Q -54 -322 -102 -298 Q -150 -320 -200 -300 Z" fill={o.umbrella} />
					<path d="M -200 -300 Q -4 -440 196 -300" stroke="#fff" strokeOpacity={0.12} strokeWidth={6} fill="none" />
				</g>
			)}
		</g>
	);
};

// ---------------- the kid ----------------
const K = {torso: 150, neck: 14, ua: 78, fa: 74, th: 112, sh: 108};
export const KID = {skin: '#a06b46', shade: '#80522f', coat: '#f2b42c', coatShade: '#d4921a', uniform: '#f3f3ef', bag: '#2f8c55', bagShade: '#1f6b3e'};

export const KidHead: React.FC<{face?: Face; drops?: boolean}> = ({face = {}, drops = true}) => {
	const sm = face.smile ?? 1;
	const lk = face.look ?? 0;
	const open = face.open ?? 0;
	return (
		<g>
			{/* hood back */}
			<path d="M -48 -26 Q -60 -104 -2 -124 Q 54 -136 68 -82 Q 72 -62 62 -50 Q 56 -30 40 -18 Q 0 6 -40 -6 Z" fill={KID.coat} />
			<path d="M -48 -26 Q -60 -104 -2 -124 Q 54 -136 68 -82 Q 72 -62 62 -50 Q 56 -30 40 -18 Q 0 6 -40 -6 Z" fill="url(#lit)" />
			{/* face */}
			<path d="M -22 -42 Q -26 -86 6 -96 Q 40 -102 50 -70 Q 54 -58 52 -48 Q 57 -42 52 -36 Q 50 -14 36 -4 Q 22 6 6 2 Q -14 -2 -20 -16 Q -24 -28 -22 -42 Z" fill={KID.skin} />
			<path d="M -22 -42 Q -26 -86 6 -96 Q 40 -102 50 -70 Q 54 -58 52 -48 Q 57 -42 52 -36 Q 50 -14 36 -4 Q 22 6 6 2 Q -14 -2 -20 -16 Q -24 -28 -22 -42 Z" fill="url(#lit)" />
			{/* fringe */}
			<path d="M -6 -86 Q 14 -98 46 -82 Q 36 -80 28 -82 Q 22 -74 12 -78 Q 2 -72 -6 -86 Z" fill="#17110d" />
			{/* cheeks */}
			<circle cx={16} cy={-32} r={9} fill="#d0745a" opacity={0.3} />
			<circle cx={49} cy={-33} r={4} fill="#d0745a" opacity={0.3} />
			{/* eyes (happy squint when smiling) */}
			<path d="M 12 -51 Q 22 -60 32 -51 Q 22 -45 12 -51 Z" fill="#f4efe6" />
			<circle cx={23 + lk * 4} cy={-51.5} r={5.2} fill="#24150d" />
			<circle cx={21 + lk * 4} cy={-54} r={1.7} fill="#fff" />
			<path d="M 11 -51 Q 22 -61 33 -52" stroke="#1a0f09" strokeWidth={2.6} fill="none" strokeLinecap="round" />
			<path d={`M 13 -47 Q 22 ${-44 - sm * 3} 31 -48`} stroke={KID.shade} strokeWidth={1.8} fill="none" opacity={0.8} />
			<path d="M 40 -51 Q 45 -57 50 -51 Q 45 -47 40 -51 Z" fill="#f4efe6" />
			<circle cx={45.5 + lk * 2} cy={-51.5} r={3.4} fill="#24150d" />
			<path d="M 39 -51 Q 45 -58 51 -52" stroke="#1a0f09" strokeWidth={2} fill="none" />
			{/* brows */}
			<path d="M 12 -63 Q 22 -68 31 -64" stroke="#1b120c" strokeWidth={3} fill="none" strokeLinecap="round" />
			<path d="M 40 -64 Q 45 -66 50 -63" stroke="#1b120c" strokeWidth={2.4} fill="none" strokeLinecap="round" />
			{/* nose */}
			<path d="M 48 -46 Q 54 -40 50 -36" stroke={KID.shade} strokeWidth={2.2} fill="none" strokeLinecap="round" />
			{/* mouth: warm smile, optionally open (talking) */}
			{open > 0 || sm > 0.6 ? (
				<g>
					<path d={`M 27 -25 Q 38 ${-13 + open * 6} 49 -26 Q 38 -21 27 -25 Z`} fill="#5a1d14" />
					<path d="M 29 -24.5 Q 38 -20.5 47 -25 L 46 -22.5 Q 38 -19 30 -22 Z" fill="#fbf6ee" />
				</g>
			) : (
				<path d="M 29 -24 Q 38 -19 47 -25" stroke="#5a2a1c" strokeWidth={2.4} fill="none" strokeLinecap="round" />
			)}
			{/* hood brim over forehead */}
			<path d="M -26 -40 Q -30 -96 10 -106 Q 50 -112 62 -70" stroke={KID.coat} strokeWidth={16} fill="none" strokeLinecap="round" />
			<path d="M -22 -44 Q -24 -92 10 -100 Q 46 -105 56 -70" stroke={KID.coatShade} strokeWidth={3} fill="none" />
			<path d="M -36 -60 Q -30 -108 14 -118" stroke="#fff" strokeOpacity={0.35} strokeWidth={4} fill="none" strokeLinecap="round" />
			{drops && [[-34, -84, 3.4], [-12, -110, 3], [14, -117, 3.6], [38, -110, 2.8], [-40, -50, 2.6], [56, -92, 2.4], [-22, -100, 2.2], [30, -118, 2]].map(([dx, dy, r], i) => <Drop key={i} x={dx} y={dy} r={r} />)}
		</g>
	);
};

export const Kid: React.FC<{p: Pose; face?: Face; s?: number; dir?: 1 | -1; x?: number; y?: number; raincoat?: boolean; bagCover?: boolean}> = ({p, face = {}, s = 1, dir = 1, x = 0, y = 0, raincoat = true, bagCover = true}) => {
	const neckBase: V = [K.torso * Math.sin(p.t * R), -K.torso * Math.cos(p.t * R)];
	const shoulder: V = add(neckBase, [0, 18]);
	const elbow = add(shoulder, dirv(p.ua, K.ua));
	const wrist = add(elbow, dirv(p.fa, K.fa));
	const elbow2 = add(shoulder, dirv(p.ua2, K.ua));
	const wrist2 = add(elbow2, dirv(p.fa2, K.fa));
	const knee = add([4, 0], dirv(p.th, K.th));
	const ankle = add(knee, dirv(p.sh, K.sh));
	const knee2 = add([-4, 0], dirv(p.th2, K.th));
	const ankle2 = add(knee2, dirv(p.sh2, K.sh));
	const coat = raincoat ? KID.coat : KID.uniform;
	const coatShade = raincoat ? KID.coatShade : '#d8dadc';
	const Leg = ({k, a, th, sh, foot, far}: {k: V; a: V; th: number; sh: number; foot: number; far?: boolean}) => (
		<g style={far ? {filter: "brightness(0.82)"} : undefined}>
			<g transform={`translate(${far ? -4 : 4},0) rotate(${-th})`}>
				<path d={limbPath(K.th, 44, 30, 2)} fill={KID.skin} />
				<path d={`M -24 -6 L 24 -6 L 22 ${K.th * 0.55} L -22 ${K.th * 0.55} Z`} fill={KID.uniform} />
				<path d={limbPath(K.th, 44, 30, 2)} fill="url(#lit)" />
			</g>
			<g transform={`translate(${k[0]},${k[1]}) rotate(${-sh})`}>
				<path d={limbPath(K.sh, 30, 22, 2)} fill={KID.skin} />
				<path d={`M -14 ${K.sh * 0.45} L 14 ${K.sh * 0.45} L 12 ${K.sh} L -12 ${K.sh} Z`} fill="#f4f4f0" />
				<path d={`M -14 ${K.sh * 0.45} L 14 ${K.sh * 0.45}`} stroke="#c9cbcf" strokeWidth={3} />
				<path d={limbPath(K.sh, 30, 22, 2)} fill="url(#lit)" />
			</g>
			<g transform={`translate(${a[0]},${a[1] + 4}) rotate(${foot})`}>
				<path d="M -15 -4 L 10 -5 Q 24 2 38 6 Q 46 10 45 18 L 45 21 L -17 21 Q -20 8 -15 -4 Z" fill="#17171a" />
				<path d="M 14 0 Q 28 4 38 9" stroke="#fff" strokeOpacity={0.35} strokeWidth={2.5} fill="none" />
			</g>
		</g>
	);
	const Arm = ({sh0, e, w, ua, fa, near}: {sh0: V; e: V; w: V; ua: number; fa: number; near: boolean}) => (
		<g style={near ? undefined : {filter: "brightness(0.82)"}}>
			<g transform={`translate(${sh0[0]},${sh0[1]}) rotate(${-ua})`}>
				<path d={limbPath(K.ua + 6, 36, 32, 3)} fill={coat} />
				<path d={limbPath(K.ua + 6, 36, 32, 3)} fill="url(#lit)" />
				<path d={`M -16 ${K.ua - 2} Q 0 ${K.ua + 6} 16 ${K.ua - 2}`} stroke={coatShade} strokeWidth={4} fill="none" />
			</g>
			<g transform={`translate(${e[0]},${e[1]}) rotate(${-fa})`}>
				<path d={limbPath(K.fa, 24, 19, 2)} fill={KID.skin} />
				<path d={limbPath(K.fa, 24, 19, 2)} fill="url(#lit)" />
				{near && <Scar y={22} s={0.8} />}
			</g>
			<g transform={`translate(${w[0]},${w[1]}) rotate(${-fa})`}><Hand skin={KID.skin} shade={KID.shade} s={0.68} /></g>
		</g>
	);
	const coatPath = `M -30 -${K.torso + 6} Q 0 -${K.torso + 16} 32 -${K.torso + 4} Q 42 -90 46 -10 L 56 ${raincoat ? 84 : 6} Q 0 ${raincoat ? 96 : 14} -54 ${raincoat ? 84 : 6} L -40 -10 Q -42 -90 -30 -${K.torso + 6} Z`;
	return (
		<g transform={`translate(${x},${y}) scale(${dir * s},${s})`}>
			<Arm sh0={add(shoulder, [-6, 0])} e={elbow2} w={wrist2} ua={p.ua2} fa={p.fa2} near={false} />
			<Leg k={knee2} a={ankle2} th={p.th2} sh={p.sh2} foot={p.foot2} far />
			<Leg k={knee} a={ankle} th={p.th} sh={p.sh} foot={p.foot} />
			<g transform={`rotate(${p.t})`}>
				{/* school bag with green rain cover */}
				<path d={`M -34 -${K.torso - 4} Q -92 -${K.torso} -92 -90 L -90 -24 Q -88 -6 -40 -8 Z`} fill={KID.bag} />
				<path d={`M -40 -${K.torso - 10} Q -84 -${K.torso - 8} -84 -90 L -82 -26 Q -80 -14 -42 -16`} stroke={KID.bagShade} strokeWidth={3} fill="none" strokeDasharray="5 4" />
				<path d={`M -80 -${K.torso - 20} Q -86 -100 -80 -60`} stroke="#fff" strokeOpacity={0.35} strokeWidth={5} fill="none" strokeLinecap="round" />
				{bagCover && [[-70, -120, 3], [-56, -70, 2.6], [-78, -44, 2.4]].map(([dx, dy, r], i) => <Drop key={i} x={dx} y={dy} r={r} />)}
				<path d={coatPath} fill={coat} />
				<path d={coatPath} fill="url(#lit)" />
				{/* white uniform collar at the neck opening */}
				<path d={`M -6 -${K.torso + 8} L 22 -${K.torso + 6} L 14 -${K.torso - 30} Z`} fill={KID.uniform} />
				<path d={`M -6 -${K.torso + 8} L 6 -${K.torso - 14} L 14 -${K.torso + 4} Z M 22 -${K.torso + 6} L 18 -${K.torso - 14} L 12 -${K.torso + 4} Z`} fill="#ffffff" stroke="#d0d2d5" strokeWidth={1.2} />
				{raincoat && (
					<g>
						<path d={`M 18 -${K.torso - 28} Q 30 -60 34 86`} stroke={KID.coatShade} strokeWidth={2.5} fill="none" />
						{[-100, -60, -20, 20, 60].map((by) => <circle key={by} cx={26 + (by + 100) * 0.05} cy={by} r={3.2} fill="#c97f12" />)}
						<path d="M -36 40 Q 0 50 52 40" stroke={KID.coatShade} strokeWidth={2} fill="none" opacity={0.7} />
						<path d={`M -20 -${K.torso - 10} Q -26 -80 -22 60`} stroke="#fff" strokeOpacity={0.3} strokeWidth={6} fill="none" strokeLinecap="round" />
						{[[-10, -110, 2.6], [30, -40, 2.4], [-24, 20, 2.8], [8, 66, 2.2]].map(([dx, dy, r], i) => <Drop key={i} x={dx} y={dy} r={r} />)}
					</g>
				)}
				{/* bag strap */}
				<path d={`M 2 -${K.torso + 6} Q 4 -120 -2 -84`} stroke={KID.bagShade} strokeWidth={9} fill="none" strokeLinecap="round" />
			</g>
			<g transform={`translate(${neckBase[0]},${neckBase[1]}) rotate(${p.t + p.neck})`}>
				<rect x={-10} y={-K.neck - 4} width={22} height={K.neck + 8} fill={KID.shade} />
				<g transform={`translate(2,-${K.neck - 2}) rotate(${p.head})`}>
					{raincoat ? <KidHead face={face} /> : <KidHeadBare face={face} />}
				</g>
			</g>
			<Arm sh0={shoulder} e={elbow} w={wrist} ua={p.ua} fa={p.fa} near />
		</g>
	);
};

// the same boy, years earlier, on a sunny day (no hood)
export const KidHeadBare: React.FC<{face?: Face}> = ({face = {}}) => (
	<g>
		<path d="M -18 -50 Q -30 -54 -28 -40 Q -26 -28 -16 -30 Z" fill={KID.skin} />
		<g>
			<KidHeadFaceOnly face={face} />
		</g>
		<path d="M -24 -40 Q -32 -96 8 -104 Q 46 -110 54 -72 Q 48 -82 36 -84 Q 26 -76 14 -82 Q 4 -74 -8 -78 Q -14 -64 -14 -50 Q -20 -48 -24 -40 Z" fill="#17110d" />
	</g>
);
const KidHeadFaceOnly: React.FC<{face?: Face}> = ({face}) => {
	// reuse the hooded head but hide the hood by drawing only the face layers
	return (
		<g>
			<g clipPath="url(#kidFaceClip)">
				<KidHead face={face} drops={false} />
			</g>
			<defs>
				<clipPath id="kidFaceClip">
					<path d="M -22 -42 Q -26 -86 6 -96 Q 40 -102 50 -70 Q 54 -58 52 -48 Q 57 -42 52 -36 Q 50 -14 36 -4 Q 22 6 6 2 Q -14 -2 -20 -16 Q -24 -28 -22 -42 Z" />
				</clipPath>
			</defs>
		</g>
	);
};

// ---------------- poses ----------------
export const POSES = {
	stand: pose(),
	lookBack: pose({t: -2, neck: -6, head: -4}),
	waiting: pose({ua: 2, fa: 6, ua2: -2, fa2: 4, th: 2, sh: 0, th2: -4, sh2: -4}),
	worriedStand: pose({t: 6, neck: 10, head: 6, ua: 10, fa: 30, ua2: 4, fa2: 24}),
};
