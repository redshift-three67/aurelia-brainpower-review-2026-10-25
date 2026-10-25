import { useGLTF } from '@react-three/drei';

export const AVAILABLE_MODELS = {
  fullBody: '/models/human-body.glb',
} as const;

export function preloadModels() {
  Object.values(AVAILABLE_MODELS).forEach((path) => {
    try { useGLTF.preload(path); } catch { /* not yet */ }
  });
}
