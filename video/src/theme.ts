import {continueRender, delayRender, staticFile} from 'remotion';

export const colors = {
  navy: '#0B2545',
  forest: '#1E5631',
  white: '#FFFFFF',
  orange: '#F57C1F',
};

export const fontFamily = 'Inter, sans-serif';

const faces: [string, string][] = [
  ['600', 'fonts/Inter-SemiBold.otf'],
  ['800', 'fonts/Inter-ExtraBold.otf'],
  ['900', 'fonts/Inter-Black.otf'],
];

const handle = delayRender('Carregando fontes');
Promise.all(
  faces.map(([weight, file]) => {
    const face = new FontFace('Inter', `url(${staticFile(file)})`, {weight});
    document.fonts.add(face);
    return face.load();
  }),
).then(() => continueRender(handle));
