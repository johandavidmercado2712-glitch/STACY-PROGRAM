// Generado: iconos Phosphor usados por el sitio (subset de @phosphor-icons/core).
import type { IconWeight } from './types';

const raw = {
  'regular/arrow-right': () => import('./regular/arrow-right.svg?raw'),
  'regular/arrow-square-out': () => import('./regular/arrow-square-out.svg?raw'),
  'regular/check-circle': () => import('./regular/check-circle.svg?raw'),
  'regular/clock-counter-clockwise': () => import('./regular/clock-counter-clockwise.svg?raw'),
  'regular/desktop-tower': () => import('./regular/desktop-tower.svg?raw'),
  'regular/download-simple': () => import('./regular/download-simple.svg?raw'),
  'regular/folder-open': () => import('./regular/folder-open.svg?raw'),
  'regular/laptop': () => import('./regular/laptop.svg?raw'),
  'regular/monitor': () => import('./regular/monitor.svg?raw'),
  'regular/moon': () => import('./regular/moon.svg?raw'),
  'regular/sun': () => import('./regular/sun.svg?raw'),
  'regular/note-pencil': () => import('./regular/note-pencil.svg?raw'),
  'regular/terminal-window': () => import('./regular/terminal-window.svg?raw'),
  'regular/x-circle': () => import('./regular/x-circle.svg?raw'),
  'bold/arrow-right': () => import('./bold/arrow-right.svg?raw'),
  'bold/arrow-square-out': () => import('./bold/arrow-square-out.svg?raw'),
  'bold/check-circle': () => import('./bold/check-circle.svg?raw'),
  'bold/clock-counter-clockwise': () => import('./bold/clock-counter-clockwise.svg?raw'),
  'bold/desktop-tower': () => import('./bold/desktop-tower.svg?raw'),
  'bold/download-simple': () => import('./bold/download-simple.svg?raw'),
  'bold/folder-open': () => import('./bold/folder-open.svg?raw'),
  'bold/laptop': () => import('./bold/laptop.svg?raw'),
  'bold/monitor': () => import('./bold/monitor.svg?raw'),
  'bold/moon': () => import('./bold/moon.svg?raw'),
  'bold/sun': () => import('./bold/sun.svg?raw'),
  'bold/note-pencil': () => import('./bold/note-pencil.svg?raw'),
  'bold/terminal-window': () => import('./bold/terminal-window.svg?raw'),
  'bold/x-circle': () => import('./bold/x-circle.svg?raw'),
  'fill/arrow-right': () => import('./fill/arrow-right.svg?raw'),
  'fill/arrow-square-out': () => import('./fill/arrow-square-out.svg?raw'),
  'fill/check-circle': () => import('./fill/check-circle.svg?raw'),
  'fill/clock-counter-clockwise': () => import('./fill/clock-counter-clockwise.svg?raw'),
  'fill/desktop-tower': () => import('./fill/desktop-tower.svg?raw'),
  'fill/download-simple': () => import('./fill/download-simple.svg?raw'),
  'fill/folder-open': () => import('./fill/folder-open.svg?raw'),
  'fill/laptop': () => import('./fill/laptop.svg?raw'),
  'fill/monitor': () => import('./fill/monitor.svg?raw'),
  'fill/moon': () => import('./fill/moon.svg?raw'),
  'fill/sun': () => import('./fill/sun.svg?raw'),
  'fill/note-pencil': () => import('./fill/note-pencil.svg?raw'),
  'fill/terminal-window': () => import('./fill/terminal-window.svg?raw'),
  'fill/x-circle': () => import('./fill/x-circle.svg?raw'),
};

export type IconName =
  | 'arrow-right'
  | 'arrow-square-out'
  | 'check-circle'
  | 'clock-counter-clockwise'
  | 'desktop-tower'
  | 'download-simple'
  | 'folder-open'
  | 'laptop'
  | 'monitor'
  | 'moon'
  | 'note-pencil'
  | 'sun'
  | 'terminal-window'
  | 'x-circle'
;

export async function loadIcon(weight: IconWeight, name: string): Promise<string> {
  const loader = raw[`${weight}/${name}`];
  if (!loader) return '';
  return (await loader()).default as string;
}
