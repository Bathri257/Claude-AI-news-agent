import React from 'react';
import {Composition, AbsoluteFill, useCurrentFrame, interpolate} from 'remotion';
const Test: React.FC = () => {
  const f = useCurrentFrame();
  return <AbsoluteFill style={{background:'#1d2b45',justifyContent:'center',alignItems:'center'}}>
    <div style={{color:'#ffd9a0',fontSize:90,opacity:interpolate(f,[0,30],[0,1])}}>Pipeline OK</div>
  </AbsoluteFill>;
};
export const RemotionRoot: React.FC = () => (
  <Composition id="Story" component={Test} durationInFrames={60} fps={30} width={1080} height={1920} />
);
