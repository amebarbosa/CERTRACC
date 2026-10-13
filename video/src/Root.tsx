import {Composition} from 'remotion';
import {CuidarDoSeuFilho, DURATION} from './CuidarDoSeuFilho';

export const RemotionRoot: React.FC = () => (
  <Composition
    id="CuidarDoSeuFilho"
    component={CuidarDoSeuFilho}
    durationInFrames={DURATION}
    fps={30}
    width={1080}
    height={1920}
  />
);
