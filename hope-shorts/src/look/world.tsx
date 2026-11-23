// Environment, vehicles and camera for the OMR scenes.  Units: 400 = 1 metre.
import React, {useMemo} from 'react';
import {random} from 'remotion';

// ---------------- camera / perspective ----------------
export type Cam = {f: number; h: number; horizon: number; cx?: number; x?: number};
export const proj = (c: Cam, x: number, z: number, y = 0) => ({
	sx: (c.cx ?? 540) + (c.f * (x - (c.x ?? 0))) / z,
	sy: c.horizon + (c.f * (c.h - y)) / z,
	ppm: c.f / z,
});
export const Placed: React.FC<{c: Cam; x: number; z: number; y?: number; blur?: number; motion?: number; flip?: boolean; children: React.ReactNode; opacity?: number}> = ({c, x, z, y = 0, blur = 0, motion = 0, flip, children, opacity = 1}) => {
	const p = proj(c, x, z, y);
	const s = p.ppm / 400;
	const inner = <g transform={`translate(${p.sx},${p.sy}) scale(${flip ? -s : s},${s})`}>{children}</g>;
	if (!blur && !motion) return <g opacity={opacity}>{inner}</g>;
	return (
		<g opacity={opacity} style={{filter: `url(#b_${Math.round(blur)}_${Math.round(motion)})`}}>
			{inner}
		</g>
	);
};
// declare every blur combo a shot uses
export const BlurDefs: React.FC<{list: [number, number][]}> = ({list}) => (
	<defs>
		{list.map(([b, m]) => (
			<filter key={`${b}_${m}`} id={`b_${b}_${m}`} x="-60%" y="-60%" width="220%" height="220%">
				<feGaussianBlur stdDeviation={`${b + m} ${b}`} />
			</filter>
		))}
	</defs>
);

// ---------------- the bike: dark-blue dual-purpose commuter, white tank, black seat (no branding) ----------------
const BIKE = {blue: '#1c3558', blue2: '#2b4c7c', white: '#eeeeea', whiteShade: '#c6cad0', black: '#141416', steel: '#a9afb7', steelDark: '#6c727a'};
const SpokedWheel: React.FC<{cx: number; cy: number; r: number; rot?: number; disc?: boolean}> = ({cx, cy, r, rot = 0, disc}) => (
	<g transform={`translate(${cx},${cy})`}>
		<circle r={r - 13} fill="none" stroke="#18181b" strokeWidth={26} />
		<circle r={r - 1} fill="none" stroke="#18181b" strokeWidth={7} strokeDasharray="11 7" transform={`rotate(${rot})`} />
		<circle r={r - 26} fill="none" stroke={BIKE.steel} strokeWidth={6} />
		<circle r={r - 30} fill="none" stroke="#3a3d42" strokeWidth={2} />
		<g transform={`rotate(${rot})`}>
			{new Array(18).fill(0).map((_, i) => {
				const a = (i * 20 * Math.PI) / 180;
				const off = i % 2 ? 0.22 : -0.22;
				return <line key={i} x1={Math.cos(a + off) * 18} y1={Math.sin(a + off) * 18} x2={Math.cos(a) * (r - 29)} y2={Math.sin(a) * (r - 29)} stroke="#b9bec5" strokeWidth={1.8} />;
			})}
		</g>
		{disc ? (
			<g>
				<circle r={58} fill="none" stroke="#c4c8ce" strokeWidth={14} />
				{new Array(10).fill(0).map((_, i) => <circle key={i} cx={Math.cos(i * 0.628 + rot / 57) * 58} cy={Math.sin(i * 0.628 + rot / 57) * 58} r={3} fill="#555" />)}
				<path d="M 28 -62 Q 58 -70 70 -40 L 52 -32 Q 44 -50 26 -48 Z" fill="#2a2c31" />
			</g>
		) : (
			<circle r={40} fill="#3e4148" />
		)}
		<circle r={20} fill={BIKE.steel} />
		<circle r={8} fill="#2a2c30" />
	</g>
);

export const Bike: React.FC<{wr?: number; light?: boolean; drops?: boolean}> = ({wr = 0, light = true, drops = true}) => (
	<g>
		{/* far-side grip & mirror (slightly darker) */}
		<path d="M 118 -452 L 84 -472" stroke="#0e0e10" strokeWidth={14} strokeLinecap="round" />
		{/* rear wheel + swingarm + chain */}
		<SpokedWheel cx={-282} cy={-130} r={130} rot={wr} />
		<path d="M -40 -214 L -282 -134" stroke="#2b2e33" strokeWidth={28} strokeLinecap="round" />
		<path d="M -40 -214 L -282 -134" stroke="#5a5f67" strokeWidth={6} strokeLinecap="round" transform="translate(0,-8)" />
		<circle cx={-282} cy={-130} r={46} fill="none" stroke="#3b3e44" strokeWidth={6} strokeDasharray="5 4" />
		<path d="M -20 -218 L -282 -176 M -20 -182 L -282 -84" stroke="#3b3e44" strokeWidth={4} />
		{/* rear shock */}
		<g transform="translate(-120,-190) rotate(25)">
			<rect x={-9} y={-150} width={18} height={150} rx={5} fill="#555a61" />
			{new Array(9).fill(0).map((_, i) => <rect key={i} x={-14} y={-140 + i * 15} width={28} height={6} rx={3} fill="#c8392f" />)}
		</g>
		{/* frame */}
		<path d="M 146 -405 L 112 -175 M 146 -405 L -40 -345 L -40 -205" stroke="#202227" strokeWidth={20} fill="none" strokeLinejoin="round" />
		{/* engine */}
		<path d="M 108 -292 L 122 -176 Q 40 -150 -32 -162 L -40 -270 Q 30 -300 108 -292 Z" fill="#33363c" />
		{new Array(6).fill(0).map((_, i) => <line key={i} x1={44 + i * 2} y1={-300 + i * 13} x2={112 + i * 2} y2={-300 + i * 13} stroke="#4c5058" strokeWidth={6} />)}
		<circle cx={30} cy={-212} r={44} fill="#8d939b" />
		<circle cx={30} cy={-212} r={44} fill="url(#litDisc)" />
		<circle cx={30} cy={-212} r={26} fill="none" stroke="#6b7179" strokeWidth={3} />
		{/* exhaust */}
		<path d="M 112 -262 Q 150 -200 120 -158 Q 60 -128 -40 -150 Q -120 -170 -170 -238" stroke="#7d838b" strokeWidth={16} fill="none" strokeLinecap="round" />
		<path d="M -150 -226 L -312 -296 L -322 -268 L -166 -198 Z" fill="#202227" />
		<path d="M -150 -226 L -312 -296" stroke="#9aa0a8" strokeWidth={5} />
		<ellipse cx={-318} cy={-282} rx={9} ry={16} fill="#5d6269" transform="rotate(24 -318 -282)" />
		{/* rear tail + side panel + seat */}
		<path d="M -40 -352 L -238 -338 Q -248 -310 -226 -296 L -70 -300 Z" fill={BIKE.blue} />
		<path d="M -60 -330 L -218 -322" stroke={BIKE.white} strokeWidth={7} strokeLinecap="round" opacity={0.9} />
		<path d="M -238 -356 L -352 -372 L -348 -356 L -240 -334 Z" fill={BIKE.blue} />
		<path d="M -330 -372 L -352 -374 L -350 -358 L -328 -360 Z" fill="#d12d2d" />
		<path d="M -6 -376 L -250 -358 Q -262 -350 -250 -342 L -6 -352 Z" fill={BIKE.black} />
		<path d="M -20 -374 L -236 -357" stroke="#fff" strokeOpacity={0.14} strokeWidth={4} />
		<path d="M -210 -350 L -244 -300" stroke="#26282d" strokeWidth={8} />
		{/* tank (white with blue graphic) + shroud */}
		<path d="M 150 -390 L 118 -296 L 36 -306 L 70 -352 Z" fill={BIKE.blue} />
		<path d="M 128 -414 Q 60 -440 -12 -378 L -18 -340 Q 46 -318 116 -336 Z" fill={BIKE.white} />
		<path d="M 128 -414 Q 60 -440 -12 -378 L -18 -340 Q 46 -318 116 -336 Z" fill="url(#litV2)" />
		<path d="M 110 -350 Q 50 -360 -4 -350 L -10 -340 Q 50 -326 114 -338 Z" fill={BIKE.blue2} />
		<path d="M 120 -396 Q 70 -380 20 -388" stroke={BIKE.blue} strokeWidth={8} fill="none" strokeLinecap="round" />
		<path d="M 100 -420 Q 60 -428 20 -398" stroke="#fff" strokeWidth={6} fill="none" opacity={0.8} strokeLinecap="round" />
		{/* front fork with gaiters */}
		<path d="M 146 -405 L 282 -138" stroke={BIKE.steel} strokeWidth={22} strokeLinecap="round" />
		<path d="M 190 -318 L 236 -228" stroke="#18191c" strokeWidth={30} strokeLinecap="butt" />
		{new Array(6).fill(0).map((_, i) => {
			const k = i / 5;
			const x = 190 + 46 * k;
			const y = -318 + 90 * k;
			return <line key={i} x1={x - 14} y1={y + 6} x2={x + 14} y2={y - 8} stroke="#33363b" strokeWidth={4} />;
		})}
		<SpokedWheel cx={282} cy={-138} r={138} rot={wr} disc />
		{/* high front fender */}
		<path d="M 180 -326 Q 230 -352 300 -330 L 296 -316 Q 236 -334 186 -312 Z" fill={BIKE.blue} />
		{/* headlight cowl + lamp */}
		<path d="M 168 -446 Q 228 -436 236 -388 Q 238 -350 214 -338 L 176 -350 Z" fill={BIKE.blue} />
		<ellipse cx={214} cy={-388} rx={14} ry={26} fill={light ? '#fff6d8' : '#d8d6cc'} />
		<path d="M 172 -444 Q 214 -440 230 -410" stroke="#fff" strokeOpacity={0.25} strokeWidth={5} fill="none" />
		{/* bars, mirror, near grip */}
		<path d="M 128 -440 L 128 -462 L 70 -476" stroke="#1b1c20" strokeWidth={9} fill="none" strokeLinecap="round" strokeLinejoin="round" />
		<path d="M 92 -472 L 62 -478" stroke="#0d0d0f" strokeWidth={16} strokeLinecap="round" />
		<path d="M 118 -466 L 108 -512" stroke="#1b1c20" strokeWidth={5} />
		<ellipse cx={104} cy={-520} rx={20} ry={13} fill="#1b1c20" transform="rotate(-12 104 -520)" />
		<rect x={128} y={-470} width={30} height={20} rx={4} fill="#202227" />
		{/* footpeg + stand */}
		<rect x={-50} y={-160} width={36} height={10} rx={4} fill="#2b2d31" />
		{drops && [[60, -420, 4], [20, -396, 3], [90, -402, 3.4], [-100, -370, 3], [-180, -362, 2.6]].map(([x, y, r], i) => (
			<g key={i}><circle cx={x} cy={y} r={r} fill="#fff" fillOpacity={0.35} /><circle cx={x - 1} cy={y - 1.4} r={r * 0.35} fill="#fff" /></g>
		))}
	</g>
);
export const BikeDefs: React.FC = () => (
	<defs>
		<linearGradient id="litV2" x1="0" y1="0" x2="0" y2="1">
			<stop offset="0" stopColor="#fff" stopOpacity="0.3" />
			<stop offset="1" stopColor="#5a6676" stopOpacity="0.35" />
		</linearGradient>
		<radialGradient id="litDisc" cx="0.35" cy="0.3" r="0.8">
			<stop offset="0" stopColor="#fff" stopOpacity="0.45" />
			<stop offset="1" stopColor="#000" stopOpacity="0.2" />
		</radialGradient>
		<linearGradient id="glass" x1="0" y1="0" x2="1" y2="1">
			<stop offset="0" stopColor="#5d7186" />
			<stop offset="0.45" stopColor="#2b3846" />
			<stop offset="0.5" stopColor="#7f93a6" />
			<stop offset="0.56" stopColor="#2b3846" />
			<stop offset="1" stopColor="#1f2833" />
		</linearGradient>
		<linearGradient id="carSheen" x1="0" y1="0" x2="0" y2="1">
			<stop offset="0" stopColor="#fff" stopOpacity="0.35" />
			<stop offset="0.35" stopColor="#fff" stopOpacity="0.05" />
			<stop offset="1" stopColor="#000" stopOpacity="0.3" />
		</linearGradient>
		<radialGradient id="beam" cx="0" cy="0.5" r="1">
			<stop offset="0" stopColor="#fff4d2" stopOpacity="0.55" />
			<stop offset="1" stopColor="#fff4d2" stopOpacity="0" />
		</radialGradient>
		<radialGradient id="tail" cx="0.5" cy="0.5" r="0.5">
			<stop offset="0" stopColor="#ff5a4a" stopOpacity="0.7" />
			<stop offset="1" stopColor="#ff5a4a" stopOpacity="0" />
		</radialGradient>
	</defs>
);

// ---------------- vehicles (side views, facing right; flip with Placed.flip) ----------------
const Tyre: React.FC<{x: number; r: number}> = ({x, r}) => (
	<g transform={`translate(${x},${-r})`}>
		<circle r={r} fill="#141416" />
		<circle r={r * 0.62} fill="#8e949c" />
		{[0, 72, 144, 216, 288].map((a) => <rect key={a} x={-6} y={-r * 0.6} width={12} height={r * 0.6} fill="#5d636b" transform={`rotate(${a})`} />)}
		<circle r={r * 0.18} fill="#33363b" />
	</g>
);
export const Hatchback: React.FC<{color: string}> = ({color}) => (
	<g>
		<path d="M -770 -110 L -772 -340 Q -770 -430 -715 -476 Q -630 -598 -400 -606 L 110 -606 Q 250 -598 362 -444 Q 620 -424 742 -372 Q 774 -340 772 -250 L 768 -110 Z" fill={color} />
		<path d="M -770 -110 L -772 -340 Q -770 -430 -715 -476 Q -630 -598 -400 -606 L 110 -606 Q 250 -598 362 -444 Q 620 -424 742 -372 Q 774 -340 772 -250 L 768 -110 Z" fill="url(#carSheen)" />
		<path d="M -690 -448 Q -630 -572 -400 -582 L 110 -582 Q 230 -574 330 -450 Z" fill="url(#glass)" />
		<line x1={-130} y1={-582} x2={-140} y2={-448} stroke={color} strokeWidth={22} />
		<path d="M -760 -330 L 760 -310" stroke="#000" strokeOpacity={0.18} strokeWidth={3} />
		<path d="M -140 -440 L -150 -140 M 330 -440 L 320 -160" stroke="#000" strokeOpacity={0.25} strokeWidth={3} />
		<rect x={-90} y={-372} width={60} height={12} rx={5} fill="#000" opacity={0.35} />
		<rect x={360} y={-372} width={60} height={12} rx={5} fill="#000" opacity={0.35} />
		<path d="M 300 -452 Q 330 -480 360 -470 L 360 -440 Z" fill={color} />
		<path d="M 700 -380 Q 750 -372 762 -340 L 714 -336 Z" fill="#fff3cf" />
		<path d="M -772 -440 L -748 -462 L -742 -350 L -772 -350 Z" fill="#c4241f" />
		<path d="M -720 -140 Q -490 -330 -260 -140 Z M 260 -140 Q 490 -330 720 -140 Z" fill="#101013" />
		<Tyre x={-490} r={118} />
		<Tyre x={490} r={118} />
		<path d="M -760 -130 L 760 -130" stroke="#1a1a1d" strokeWidth={26} />
	</g>
);
export const Sedan: React.FC<{color: string}> = ({color}) => (
	<g>
		<path d="M -900 -130 L -905 -330 Q -880 -380 -700 -398 Q -560 -580 -300 -590 L 160 -590 Q 320 -580 470 -420 Q 760 -404 880 -360 Q 912 -320 906 -230 L 900 -130 Z" fill={color} />
		<path d="M -900 -130 L -905 -330 Q -880 -380 -700 -398 Q -560 -580 -300 -590 L 160 -590 Q 320 -580 470 -420 Q 760 -404 880 -360 Q 912 -320 906 -230 L 900 -130 Z" fill="url(#carSheen)" />
		<path d="M -640 -410 Q -540 -560 -300 -566 L 160 -566 Q 300 -558 430 -424 Z" fill="url(#glass)" />
		<line x1={-110} y1={-566} x2={-120} y2={-420} stroke={color} strokeWidth={22} />
		<path d="M 840 -366 Q 890 -356 900 -322 L 850 -318 Z" fill="#fff3cf" />
		<path d="M -905 -360 L -870 -380 L -868 -330 L -905 -326 Z" fill="#c4241f" />
		<path d="M -820 -150 Q -580 -340 -340 -150 Z M 350 -150 Q 590 -340 830 -150 Z" fill="#101013" />
		<Tyre x={-580} r={120} />
		<Tyre x={590} r={120} />
		<path d="M -880 -140 L 880 -140" stroke="#1a1a1d" strokeWidth={24} />
	</g>
);
export const Bus: React.FC<{body?: string; band?: string}> = ({body = '#3f7f74', band = '#e9e2c9'}) => (
	<g>
		<path d="M -2200 -160 L -2200 -1180 Q -2196 -1236 -2120 -1240 L 2110 -1240 Q 2200 -1230 2206 -1120 L 2210 -160 Z" fill={body} />
		<path d="M -2200 -160 L -2200 -1180 Q -2196 -1236 -2120 -1240 L 2110 -1240 Q 2200 -1230 2206 -1120 L 2210 -160 Z" fill="url(#carSheen)" />
		<rect x={-2200} y={-760} width={4410} height={120} fill={band} />
		{new Array(9).fill(0).map((_, i) => <rect key={i} x={-2120 + i * 420} y={-1150} width={370} height={360} rx={18} fill="url(#glass)" />)}
		<rect x={1780} y={-1150} width={380} height={620} rx={18} fill="url(#glass)" />
		<rect x={1260} y={-1140} width={300} height={960} rx={10} fill="#26313a" />
		<rect x={1840} y={-1230} width={300} height={70} rx={8} fill="#1c1d20" />
		<rect x={1860} y={-1216} width={200} height={40} fill="#f2a234" opacity={0.85} />
		<path d="M -1820 -160 A 170 170 0 0 1 -1480 -160 Z M 1380 -160 A 170 170 0 0 1 1720 -160 Z" fill="#101013" />
		<Tyre x={-1650} r={150} />
		<Tyre x={1550} r={150} />
		<rect x={2150} y={-420} width={50} height={60} rx={10} fill="#fff3cf" />
		<rect x={-2210} y={-470} width={30} height={110} fill="#c4241f" />
	</g>
);
export const Auto: React.FC = () => (
	<g>
		<path d="M -470 -140 L -470 -560 Q -380 -700 60 -690 Q 300 -680 360 -520 L 420 -200 L 420 -140 Z" fill="#17181b" />
		<path d="M -490 -560 Q -400 -720 60 -712 Q 330 -700 380 -540 L 330 -548 Q 280 -660 60 -664 Q -360 -670 -440 -556 Z" fill="#17181b" />
		<path d="M -470 -330 L -470 -140 L 420 -140 L 400 -330 Z" fill="#e5b92f" />
		<path d="M 150 -620 L 340 -560 L 380 -330 L 150 -330 Z" fill="#e5b92f" />
		<path d="M 170 -600 L 320 -548 L 340 -420 L 170 -420 Z" fill="url(#glass)" opacity={0.8} />
		<path d="M -470 -330 L -470 -140 L 420 -140 L 400 -330 Z" fill="url(#carSheen)" />
		<Tyre x={-320} r={84} />
		<Tyre x={330} r={84} />
		<circle cx={400} cy={-300} r={18} fill="#fff3cf" />
	</g>
);
// a two-wheeler commuter in a raincoat (simple; usually motion-blurred)
export const Commuter: React.FC<{coat: string; scooter: string}> = ({coat, scooter}) => (
	<g>
		<Tyre x={-260} r={92} />
		<Tyre x={260} r={92} />
		<path d="M -330 -170 Q -330 -330 -150 -360 L 80 -360 Q 120 -250 230 -230 L 250 -420 L 300 -420 L 300 -200 Q 120 -150 -330 -170 Z" fill={scooter} />
		<path d="M -330 -170 Q -330 -330 -150 -360 L 80 -360 Q 120 -250 230 -230 L 250 -420 L 300 -420 L 300 -200 Q 120 -150 -330 -170 Z" fill="url(#carSheen)" />
		<path d="M -170 -380 Q -170 -560 -100 -660 Q -10 -700 50 -650 Q 100 -560 140 -470 L 230 -440 L 220 -410 L 110 -420 Q 60 -470 40 -440 L 60 -330 L -150 -330 Z" fill={coat} />
		<circle cx={-20} cy={-720} r={62} fill="#1d1f24" />
		<path d="M 20 -740 Q 60 -720 70 -690 L 30 -690 Z" fill="#3b4a5a" />
	</g>
);

// ---------------- OMR near the big glass towers ----------------
export const Towers: React.FC<{c: Cam; haze?: number; near?: number}> = ({c, haze = 0.5, near = 1}) => {
	const tower = (x: number, z: number, w: number, h: number, tint: string, seed: string) => {
		const p = proj(c, x, z);
		const top = proj(c, x, z, h);
		const W = w * p.ppm;
		const H = p.sy - top.sy;
		const floors = Math.floor(h / 3.6);
		return (
			<g key={seed}>
				<rect x={p.sx - W / 2} y={top.sy} width={W} height={H} fill={tint} />
				<rect x={p.sx - W / 2} y={top.sy} width={W} height={H} fill="url(#towerRefl)" />
				{new Array(floors).fill(0).map((_, i) => (
					<line key={i} x1={p.sx - W / 2} y1={top.sy + (i * H) / floors} x2={p.sx + W / 2} y2={top.sy + (i * H) / floors} stroke="#cfe0ea" strokeOpacity={0.18} strokeWidth={1} />
				))}
				{new Array(Math.floor(w / 1.6)).fill(0).map((_, i) => (
					<line key={'v' + i} x1={p.sx - W / 2 + (i * W) / Math.floor(w / 1.6)} y1={top.sy} x2={p.sx - W / 2 + (i * W) / Math.floor(w / 1.6)} y2={p.sy} stroke="#0d1a24" strokeOpacity={0.22} strokeWidth={1} />
				))}
				{new Array(28).fill(0).map((_, i) => {
					const fx = Math.floor(random(seed + 'wx' + i) * Math.floor(w / 1.6));
					const fy = Math.floor(random(seed + 'wy' + i) * floors);
					return <rect key={'l' + i} x={p.sx - W / 2 + (fx * W) / Math.floor(w / 1.6)} y={top.sy + (fy * H) / floors} width={W / Math.floor(w / 1.6)} height={H / floors} fill="#ffe3a8" opacity={0.35} />;
				})}
				{/* crown */}
				<rect x={p.sx - W * 0.35} y={top.sy - H * 0.04} width={W * 0.7} height={H * 0.04} fill={tint} />
				<rect x={p.sx - W * 0.35} y={top.sy - H * 0.04} width={W * 0.7} height={H * 0.04} fill="#000" opacity={0.15} />
				<line x1={p.sx} y1={top.sy - H * 0.04} x2={p.sx} y2={top.sy - H * 0.1} stroke="#4a5866" strokeWidth={3} />
			</g>
		);
	};
	return (
		<g>
			<defs>
				<linearGradient id="towerRefl" x1="0" y1="0" x2="1" y2="0.3">
					<stop offset="0" stopColor="#cfe3f0" stopOpacity="0.35" />
					<stop offset="0.35" stopColor="#cfe3f0" stopOpacity="0.05" />
					<stop offset="0.55" stopColor="#ffffff" stopOpacity="0.22" />
					<stop offset="0.65" stopColor="#cfe3f0" stopOpacity="0.02" />
					<stop offset="1" stopColor="#0a1620" stopOpacity="0.3" />
				</linearGradient>
			</defs>
			{tower(-70 * near, 420 * near, 34, 118, '#5f7f95', 'tB')}
			{tower(-20 * near, 330 * near, 40, 132, '#557891', 'tA')}
			{tower(55 * near, 380 * near, 36, 96, '#6a8799', 'tC')}
			{/* lower IT blocks */}
			{[[-120, 200, 60, 32], [40, 180, 50, 26], [110, 220, 70, 38], [-40, 160, 30, 18]].map(([x, z, w, h], i) => {
				const p = proj(c, x * near, z * near);
				const t = proj(c, x * near, z * near, h);
				const W = w * p.ppm;
				return (
					<g key={i}>
						<rect x={p.sx - W / 2} y={t.sy} width={W} height={p.sy - t.sy} fill="#b7bec4" />
						{new Array(Math.floor(h / 4)).fill(0).map((_, k) => <rect key={k} x={p.sx - W / 2} y={t.sy + 6 + k * ((p.sy - t.sy) / Math.floor(h / 4))} width={W} height={((p.sy - t.sy) / Math.floor(h / 4)) * 0.45} fill="#5d7486" opacity={0.75} />)}
					</g>
				);
			})}
			<rect x={-200} y={0} width={1480} height={c.horizon + 20} fill="#b9c3cb" opacity={haze} />
		</g>
	);
};

export const Sky: React.FC<{h: number}> = ({h}) => (
	<g>
		<defs>
			<linearGradient id="skyG" x1="0" y1="0" x2="0" y2="1">
				<stop offset="0" stopColor="#6c7b8a" />
				<stop offset="0.6" stopColor="#a7b2bc" />
				<stop offset="1" stopColor="#c8d0d6" />
			</linearGradient>
			<filter id="cloudBlur" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="40" /></filter>
		</defs>
		<rect x={-200} y={-200} width={1480} height={h + 400} fill="url(#skyG)" />
		<g filter="url(#cloudBlur)" opacity={0.55}>
			<ellipse cx={200} cy={180} rx={420} ry={110} fill="#58687a" />
			<ellipse cx={850} cy={320} rx={380} ry={90} fill="#5f6f80" />
			<ellipse cx={520} cy={520} rx={500} ry={80} fill="#d6dde2" />
		</g>
	</g>
);

// trees, footpath, curb, poles — everything on the far kerb of the road
export const Roadside: React.FC<{c: Cam; blur?: number}> = ({c, blur = 0}) => {
	const zc = 12.4; // kerb
	const zb = 15.5; // back of footpath
	const kerb = proj(c, 0, zc);
	const back = proj(c, 0, zb);
	const kerbTop = proj(c, 0, zc, 0.18);
	const stripes = [];
	for (let x = -30; x < 30; x += 0.6) {
		const a = proj(c, x, zc);
		const b = proj(c, x + 0.6, zc);
		stripes.push(<rect key={x} x={a.sx} y={kerbTop.sy} width={b.sx - a.sx + 0.5} height={kerb.sy - kerbTop.sy} fill={Math.round(x / 0.6) % 2 ? '#e2bd35' : '#1b1c1f'} />);
	}
	const trees = [-14, -6.5, 1.5, 9.5, 17];
	return (
		<g style={blur ? {filter: `url(#b_${blur}_0)`} : undefined}>
			{/* compound wall + greenery */}
			<rect x={-200} y={proj(c, 0, 19, 2.2).sy} width={1480} height={proj(c, 0, 19).sy - proj(c, 0, 19, 2.2).sy} fill="#8c8f8a" />
			<rect x={-200} y={proj(c, 0, 19, 2.2).sy} width={1480} height={6} fill="#b9bbb5" />
			{trees.map((tx, i) => {
				const base = proj(c, tx, 17);
				const top = proj(c, tx, 17, 9);
				const s = base.ppm;
				return (
					<g key={i}>
						<path d={`M ${base.sx - 0.22 * s} ${base.sy} Q ${base.sx - 0.1 * s} ${(base.sy + top.sy) / 2} ${base.sx - 0.05 * s} ${top.sy + 2 * s} L ${base.sx + 0.12 * s} ${top.sy + 2 * s} Q ${base.sx + 0.15 * s} ${(base.sy + top.sy) / 2} ${base.sx + 0.25 * s} ${base.sy} Z`} fill="#3a3430" />
						<path d={`M ${top.sx} ${top.sy + 2 * s} L ${top.sx - 1.6 * s} ${top.sy + 0.6 * s} M ${top.sx} ${top.sy + 2 * s} L ${top.sx + 1.8 * s} ${top.sy + 0.4 * s}`} stroke="#3a3430" strokeWidth={0.12 * s} />
						{new Array(26).fill(0).map((_, k) => {
							const a = random(`tr${i}a${k}`) * Math.PI * 2;
							const d = Math.sqrt(random(`tr${i}d${k}`));
							const dx = Math.cos(a) * d * 3.4;
							const dy = Math.sin(a) * d * 1.6 - 0.2;
							const r = 0.7 + random(`tr${i}r${k}`) * 0.9;
							const lightK = (1.6 - dy) / 3.2;
							const col = lightK > 0.75 ? '#5d7a4d' : lightK > 0.5 ? '#4a6640' : lightK > 0.3 ? '#3c5636' : '#2f452d';
							return <ellipse key={k} cx={top.sx + dx * s} cy={top.sy + dy * s} rx={r * s} ry={r * 0.78 * s} fill={col} />;
						})}
						{new Array(10).fill(0).map((_, k) => <circle key={'h' + k} cx={top.sx + (random(`th${i}${k}`) * 5 - 2.5) * s} cy={top.sy + (random(`tv${i}${k}`) * 1.2 - 1.4) * s} r={0.35 * s} fill="#7d9868" opacity={0.55} />)}
					</g>
				);
			})}
			{/* footpath */}
			<rect x={-200} y={back.sy} width={1480} height={kerbTop.sy - back.sy} fill="#7f838a" />
			{new Array(10).fill(0).map((_, i) => {
				const zz = zc + 0.1 + i * 0.32;
				return <line key={i} x1={-200} y1={proj(c, 0, zz, 0.18).sy} x2={1280} y2={proj(c, 0, zz, 0.18).sy} stroke="#6a6e75" strokeWidth={1} />;
			})}
			{stripes}
			{/* street lights */}
			{[-9, 6, 21].map((lx, i) => {
				const b = proj(c, lx, 13);
				const t = proj(c, lx, 13, 9);
				return (
					<g key={i}>
						<line x1={b.sx} y1={b.sy} x2={t.sx} y2={t.sy} stroke="#5b6068" strokeWidth={Math.max(2, 0.14 * b.ppm)} />
						<path d={`M ${t.sx} ${t.sy} Q ${t.sx + 0.6 * b.ppm} ${t.sy - 0.4 * b.ppm} ${t.sx + 1.6 * b.ppm} ${t.sy}`} stroke="#5b6068" strokeWidth={Math.max(2, 0.08 * b.ppm)} fill="none" />
						<rect x={t.sx + 1.3 * b.ppm} y={t.sy - 0.05 * b.ppm} width={0.6 * b.ppm} height={0.16 * b.ppm} fill="#3c4046" />
					</g>
				);
			})}
		</g>
	);
};

// wet road between the kerb and the camera, with lane lines, puddles and light streaks
export const Road: React.FC<{c: Cam; lights?: {x: number; z: number; col: string}[]}> = ({c, lights = []}) => {
	const kerb = proj(c, 0, 12.4);
	const dashes = [];
	for (let x = -40; x < 40; x += 6) {
		const a = proj(c, x, 8.6);
		const b = proj(c, x + 3, 8.6);
		dashes.push(<path key={x} d={`M ${a.sx} ${a.sy} L ${b.sx} ${b.sy} L ${b.sx} ${b.sy + 0.12 * a.ppm * (c.h / 8.6)} L ${a.sx} ${a.sy + 0.12 * a.ppm * (c.h / 8.6)} Z`} fill="#d9dbd6" opacity={0.75} />);
	}
	const puddles = useMemo(() => new Array(22).fill(0).map((_, i) => ({x: random('pdx' + i) * 30 - 15, z: 5 + random('pdz' + i) * 7, r: 0.25 + random('pdr' + i) * 0.7})), []);
	return (
		<g>
			<defs>
				<linearGradient id="roadG" x1="0" y1="0" x2="0" y2="1">
					<stop offset="0" stopColor="#5a6069" />
					<stop offset="0.25" stopColor="#3b4047" />
					<stop offset="1" stopColor="#2a2d32" />
				</linearGradient>
				<filter id="streak" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="6 22" /></filter>
			</defs>
			<rect x={-200} y={kerb.sy} width={1480} height={2400} fill="url(#roadG)" />
			{dashes}
			{puddles.map((p, i) => {
				const q = proj(c, p.x, p.z);
				const rx = p.r * q.ppm;
				const ry = rx * (c.h / p.z) * 0.9;
				return (
					<g key={i}>
						<ellipse cx={q.sx} cy={q.sy} rx={rx} ry={ry} fill="#97a6b5" opacity={0.42} />
						<ellipse cx={q.sx - rx * 0.2} cy={q.sy - ry * 0.2} rx={rx * 0.6} ry={ry * 0.4} fill="#c9d4de" opacity={0.25} />
						<ellipse cx={q.sx + rx * 0.3} cy={q.sy} rx={rx * 0.12} ry={ry * 0.18} fill="none" stroke="#e5edf3" strokeOpacity={0.5} strokeWidth={1.2} />
					</g>
				);
			})}
			{/* reflections of head/tail lights on wet asphalt */}
			<g filter="url(#streak)">
				{lights.map((l, i) => {
					const q = proj(c, l.x, l.z);
					return <ellipse key={i} cx={q.sx} cy={q.sy + 0.25 * q.ppm} rx={0.12 * q.ppm} ry={0.5 * q.ppm} fill={l.col} opacity={0.55} />;
				})}
			</g>
		</g>
	);
};

// drizzle + mist (screen space)
export const Drizzle: React.FC<{n?: number; seed?: string; len?: number; opacity?: number; near?: boolean}> = ({n = 260, seed = 'dz', len = 26, opacity = 0.35, near}) => (
	<g>
		<defs><filter id="nearDrop" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="2" /></filter></defs>
		<g style={near ? {filter: 'url(#nearDrop)'} : undefined}>
			{new Array(n).fill(0).map((_, i) => {
				const x = random(seed + 'x' + i) * 1180 - 50;
				const y = random(seed + 'y' + i) * 1980 - 30;
				const l = len * (0.6 + random(seed + 'l' + i) * 0.8) * (near ? 2.4 : 1);
				return <line key={i} x1={x} y1={y} x2={x - l * 0.16} y2={y + l} stroke="#e8eef4" strokeOpacity={opacity * (0.4 + random(seed + 'o' + i) * 0.6)} strokeWidth={near ? 3 : 1.4} strokeLinecap="round" />;
			})}
		</g>
	</g>
);

export const Grain: React.FC<{amount?: number; seed?: number}> = ({amount = 0.08, seed = 3}) => (
	<g>
		<defs>
			<filter id={`grain${seed}`}>
				<feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" seed={seed} />
				<feColorMatrix type="saturate" values="0" />
			</filter>
		</defs>
		<rect width={1080} height={1920} filter={`url(#grain${seed})`} opacity={amount} style={{mixBlendMode: 'overlay'}} />
	</g>
);

export const Glow: React.FC<{x: number; y: number; r: number; col: string; o?: number}> = ({x, y, r, col, o = 0.6}) => (
	<circle cx={x} cy={y} r={r} fill={col} opacity={o} style={{filter: `blur(${r * 0.6}px)`}} />
);
