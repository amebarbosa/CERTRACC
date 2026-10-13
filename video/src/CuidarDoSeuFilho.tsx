import React from 'react';
import {
  AbsoluteFill,
  Easing,
  Img,
  interpolate,
  Sequence,
  spring,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from 'remotion';
import {colors, fontFamily} from './theme';

const FPS = 30;
const SCENE = 5 * FPS;
export const DURATION = 4 * SCENE; // 20 s

// Fade in/out of a whole scene, so cuts between scenes are soft.
const SceneFade: React.FC<{children: React.ReactNode; bg: string; last?: boolean}> = ({
  children,
  bg,
  last,
}) => {
  const frame = useCurrentFrame();
  const opacity = last
    ? interpolate(frame, [0, 12], [0, 1], {extrapolateRight: 'clamp'})
    : interpolate(frame, [0, 12, SCENE - 12, SCENE], [0, 1, 1, 0], {
        extrapolateLeft: 'clamp',
        extrapolateRight: 'clamp',
      });
  return (
    <AbsoluteFill style={{backgroundColor: bg, opacity, fontFamily}}>{children}</AbsoluteFill>
  );
};

// A line of text that rises and fades in after `delay` frames.
const Rise: React.FC<{
  delay: number;
  children: React.ReactNode;
  style?: React.CSSProperties;
}> = ({delay, children, style}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const p = spring({frame: frame - delay, fps, config: {damping: 200}});
  return (
    <div
      style={{
        opacity: p,
        transform: `translateY(${(1 - p) * 80}px)`,
        ...style,
      }}
    >
      {children}
    </div>
  );
};

const Bar: React.FC<{delay: number; color: string; width?: number}> = ({
  delay,
  color,
  width = 260,
}) => {
  const frame = useCurrentFrame();
  const w = interpolate(frame, [delay, delay + 18], [0, width], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
    easing: Easing.out(Easing.cubic),
  });
  return <div style={{height: 16, width: w, backgroundColor: color, borderRadius: 8}} />;
};

const column: React.CSSProperties = {
  justifyContent: 'center',
  padding: '0 96px',
  gap: 36,
};

// Cena 1 — tema
const Scene1: React.FC = () => (
  <SceneFade bg={colors.navy}>
    <AbsoluteFill style={column}>
      <Rise delay={6} style={{color: colors.white, fontSize: 128, fontWeight: 900, lineHeight: 1.02}}>
        Cuidar do
        <br />
        seu filho
      </Rise>
      <Rise delay={22} style={{color: colors.orange, fontSize: 128, fontWeight: 900, lineHeight: 1.02}}>
        é a nossa
        <br />
        missão.
      </Rise>
      <Bar delay={40} color={colors.white} />
    </AbsoluteFill>
  </SceneFade>
);

// Cena 2 — especialidades
const services = ['Ortopedia', 'Reconstrução óssea', 'Alongamento'];
const Scene2: React.FC = () => (
  <SceneFade bg={colors.forest}>
    <AbsoluteFill style={column}>
      <Rise delay={4} style={{color: colors.orange, fontSize: 56, fontWeight: 800, letterSpacing: 4}}>
        NA CERTRACC
      </Rise>
      {services.map((s, i) => (
        <Rise
          key={s}
          delay={18 + i * 16}
          style={{
            color: colors.white,
            fontSize: 104,
            fontWeight: 900,
            lineHeight: 1.05,
            borderLeft: `16px solid ${colors.orange}`,
            paddingLeft: 40,
          }}
        >
          {s}
        </Rise>
      ))}
    </AbsoluteFill>
  </SceneFade>
);

// Cena 3 — acolhimento
const Scene3: React.FC = () => (
  <SceneFade bg={colors.white}>
    <AbsoluteFill style={column}>
      <Rise delay={6} style={{color: colors.navy, fontSize: 120, fontWeight: 900, lineHeight: 1.04}}>
        Cada passo
        <br />
        dele importa.
      </Rise>
      <Bar delay={26} color={colors.orange} />
      <Rise delay={36} style={{color: colors.forest, fontSize: 64, fontWeight: 800, lineHeight: 1.2}}>
        Acolhimento e cuidado
        <br />
        em todas as fases.
      </Rise>
    </AbsoluteFill>
  </SceneFade>
);

// Cena 4 — logo + @certracc
const Scene4: React.FC = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const pop = spring({frame: frame - 6, fps, config: {damping: 14, mass: 0.8}});
  return (
    <SceneFade bg={colors.navy} last>
      <AbsoluteFill style={{justifyContent: 'center', alignItems: 'center', gap: 64}}>
        <div
          style={{
            backgroundColor: colors.white,
            borderRadius: 48,
            padding: 56,
            transform: `scale(${pop})`,
            boxShadow: '0 30px 80px rgba(0,0,0,0.35)',
          }}
        >
          <Img src={staticFile('logo.png')} style={{width: 640, maxHeight: 640, objectFit: 'contain', display: 'block'}} />
        </div>
        <Rise delay={24} style={{color: colors.orange, fontSize: 112, fontWeight: 900}}>
          @certracc
        </Rise>
        <Rise
          delay={38}
          style={{color: colors.white, fontSize: 52, fontWeight: 600, textAlign: 'center', lineHeight: 1.3}}
        >
          Cuidar do seu filho
          <br />é a nossa missão.
        </Rise>
      </AbsoluteFill>
    </SceneFade>
  );
};

export const CuidarDoSeuFilho: React.FC = () => (
  <AbsoluteFill style={{backgroundColor: colors.navy}}>
    {[Scene1, Scene2, Scene3, Scene4].map((Scene, i) => (
      <Sequence key={i} from={i * SCENE} durationInFrames={SCENE}>
        <Scene />
      </Sequence>
    ))}
  </AbsoluteFill>
);
