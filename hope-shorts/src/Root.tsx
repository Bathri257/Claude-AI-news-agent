import React from 'react';
import {Composition} from 'remotion';
import {Story} from './Story';

export const RemotionRoot: React.FC = () => (
	<Composition id="Story" component={Story} durationInFrames={1800} fps={30} width={1080} height={1920} />
);
