import React from 'react';
import {Composition, Still} from 'remotion';
import {Story} from './Story';
import {CharacterSheet, Cut1, Cut2, Cut3, Cut4, Cut5, Cut6} from './look/cuts';

export const RemotionRoot: React.FC = () => (
	<>
		<Composition id="Draft1" component={Story} durationInFrames={1800} fps={30} width={1080} height={1920} />
		<Still id="Sheet" component={CharacterSheet} width={1080} height={1920} />
		<Still id="Cut1" component={Cut1} width={1080} height={1920} />
		<Still id="Cut2" component={Cut2} width={1080} height={1920} />
		<Still id="Cut3" component={Cut3} width={1080} height={1920} />
		<Still id="Cut4" component={Cut4} width={1080} height={1920} />
		<Still id="Cut5" component={Cut5} width={1080} height={1920} />
		<Still id="Cut6" component={Cut6} width={1080} height={1920} />
	</>
);
