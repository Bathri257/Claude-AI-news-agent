// Local copies of Lora + Inter (Google Fonts, SIL Open Font License) so renders work offline.
import {continueRender, delayRender, staticFile} from 'remotion';

const faces: [string, string, string][] = [
	['Lora', 'normal', 'fonts/Lora-normal.woff2'],
	['Lora', 'italic', 'fonts/Lora-italic.woff2'],
	['Inter', 'normal', 'fonts/Inter-normal.woff2'],
];
if (typeof document !== 'undefined') {
	const handle = delayRender('fonts');
	Promise.all(
		faces.map(([family, style, file]) => {
			const f = new FontFace(family, `url(${staticFile(file)}) format('woff2')`, {style, weight: '100 900'});
			return f.load().then((loaded) => document.fonts.add(loaded));
		}),
	).then(() => continueRender(handle));
}
export const LORA = 'Lora, Georgia, serif';
export const LORA_N = 'Lora, Georgia, serif';
export const INTER = 'Inter, Arial, sans-serif';
