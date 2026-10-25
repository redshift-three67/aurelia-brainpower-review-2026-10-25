/**
 * Surface-Projection System
 * Projiziert Akupunkturpunkte per Raycasting auf die Oberfläche eines 3D-Modells.
 * 
 * Strategie:
 * - Jeder Punkt hat eine ungefähre 3D-Position (aus TCM_MERIDIANS)
 * - Ein Raycast von außen nach innen (und umgekehrt) findet den nächsten Mesh-Schnittpunkt
 * - Der Punkt wird auf die Oberfläche "gesnapped"
 */
import * as THREE from 'three';

export interface ProjectedPoint {
  id: string;
  originalPosition: THREE.Vector3;
  projectedPosition: THREE.Vector3;
  surfaceNormal: THREE.Vector3;
  wasProjected: boolean; // true wenn erfolgreich auf Oberfläche projiziert
  distanceToSurface: number;
}

/**
 * Sammelt alle Meshes aus einer Three.js-Szene für Raycasting
 */
export function collectMeshes(object: THREE.Object3D): THREE.Mesh[] {
  const meshes: THREE.Mesh[] = [];
  object.traverse((child) => {
    if (child instanceof THREE.Mesh && child.geometry) {
      meshes.push(child);
    }
  });
  return meshes;
}

/**
 * Projiziert einen einzelnen Punkt auf die nächste Mesh-Oberfläche.
 * Schießt Rays von mehreren Richtungen auf den Punkt und nimmt den nächsten Treffer.
 */
export function projectPointToSurface(
  point: THREE.Vector3,
  meshes: THREE.Mesh[],
  offsetDistance: number = 0.005 // Abstand von der Oberfläche nach außen
): ProjectedPoint {
  const raycaster = new THREE.Raycaster();
  raycaster.near = 0.001;
  raycaster.far = 5;
  
  // Mehrere Raycast-Richtungen für bessere Trefferquote
  const directions = [
    new THREE.Vector3(0, 0, 1),   // von vorne
    new THREE.Vector3(0, 0, -1),  // von hinten
    new THREE.Vector3(1, 0, 0),   // von rechts
    new THREE.Vector3(-1, 0, 0),  // von links
    new THREE.Vector3(0, 1, 0),   // von oben
    new THREE.Vector3(0, -1, 0),  // von unten
    // Diagonalen
    new THREE.Vector3(0.7, 0, 0.7).normalize(),
    new THREE.Vector3(-0.7, 0, 0.7).normalize(),
    new THREE.Vector3(0, 0.7, 0.7).normalize(),
    new THREE.Vector3(0, -0.7, 0.7).normalize(),
  ];

  let closestHit: THREE.Intersection | null = null;
  let closestDistance = Infinity;

  for (const dir of directions) {
    // Ray von weit außen in Richtung des Punktes
    const origin = point.clone().add(dir.clone().multiplyScalar(2));
    const rayDir = dir.clone().negate();
    
    raycaster.set(origin, rayDir);
    const intersections = raycaster.intersectObjects(meshes, false);
    
    if (intersections.length > 0) {
      // Finde den Treffer, der am nächsten zum gewünschten Punkt liegt
      for (const hit of intersections) {
        const dist = hit.point.distanceTo(point);
        if (dist < closestDistance) {
          closestDistance = dist;
          closestHit = hit;
        }
      }
    }
  }

  if (closestHit && closestHit.face) {
    // Punkt auf Oberfläche + kleiner Offset nach außen (damit sichtbar)
    const normal = closestHit.face.normal.clone();
    // Normal in Weltkoordinaten transformieren
    if (closestHit.object instanceof THREE.Mesh) {
      normal.applyMatrix3(new THREE.Matrix3().getNormalMatrix(closestHit.object.matrixWorld));
    }
    normal.normalize();
    
    const projected = closestHit.point.clone().add(normal.clone().multiplyScalar(offsetDistance));
    
    return {
      id: '',
      originalPosition: point.clone(),
      projectedPosition: projected,
      surfaceNormal: normal,
      wasProjected: true,
      distanceToSurface: closestDistance,
    };
  }

  // Kein Treffer – Original-Position beibehalten
  return {
    id: '',
    originalPosition: point.clone(),
    projectedPosition: point.clone(),
    surfaceNormal: new THREE.Vector3(0, 0, 1),
    wasProjected: false,
    distanceToSurface: -1,
  };
}

/**
 * Projiziert eine Reihe von Meridian-Punkten auf die Mesh-Oberfläche.
 * Berücksichtigt die Meridian-X-Skalierung.
 */
export function projectMeridianPoints(
  acupoints: Array<{ id: string; position: THREE.Vector3 }>,
  meshes: THREE.Mesh[],
  meridianXScale: number = 1,
  surfaceOffset: number = 0.008
): Map<string, ProjectedPoint> {
  const projectedMap = new Map<string, ProjectedPoint>();
  
  if (meshes.length === 0) return projectedMap;

  for (const acu of acupoints) {
    // Skalierte Position anwenden (wie im MeridianSystemModel)
    const scaledPos = new THREE.Vector3(
      acu.position.x * meridianXScale,
      acu.position.y,
      acu.position.z
    );

    const result = projectPointToSurface(scaledPos, meshes, surfaceOffset);
    result.id = acu.id;
    projectedMap.set(acu.id, result);
  }

  return projectedMap;
}

/**
 * Projiziert einen ganzen Meridian-Pfad auf die Oberfläche.
 * Interpoliert zwischen projizierten Punkten für eine glatte Linie.
 */
export function projectMeridianPath(
  pathPoints: THREE.Vector3[],
  meshes: THREE.Mesh[],
  meridianXScale: number = 1,
  surfaceOffset: number = 0.006
): THREE.Vector3[] {
  if (meshes.length === 0) return pathPoints;

  return pathPoints.map(point => {
    const scaledPos = new THREE.Vector3(
      point.x * meridianXScale,
      point.y,
      point.z
    );
    
    const result = projectPointToSurface(scaledPos, meshes, surfaceOffset);
    return result.wasProjected ? result.projectedPosition : scaledPos;
  });
}

/**
 * Berechnet ob ein GLB-Modell für Surface-Projection bereit ist
 * (genügend Geometrie-Daten vorhanden)
 */
export function isMeshSufficientForProjection(meshes: THREE.Mesh[]): boolean {
  let totalVertices = 0;
  for (const mesh of meshes) {
    const geo = mesh.geometry;
    if (geo.attributes.position) {
      totalVertices += geo.attributes.position.count;
    }
  }
  // Mindestens 100 Vertices für sinnvolle Projektion
  return totalVertices >= 100;
}
