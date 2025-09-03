function clamp(v, lo=-1, hi=1) { return Math.min(hi, Math.max(lo, v)); }
function dz(v, d=0.05) { return Math.abs(v) < d ? 0 : v; }

// scale [-1..1] -> int16 [-32767..32767]
function toInt16Norm(v) {
  const n = Math.round(clamp(v) * 32767);
  return Math.max(-32767, Math.min(32767, n));
}

/**
 * Returns [x, y, z, r] for MANUAL_CONTROL:
 * x: fwd/back   (-1..1)  (+ = forward)
 * y: left/right (-1..1)  (+ = right)
 * z: up/down    (-1..1)  (+ = up)    // note: MC expects -1=down, +1=up
 * r: yaw        (-1..1)  (+ = clockwise)
 */
export function getRCInput() {
  const pads = navigator.getGamepads?.();
  const gp = pads && pads[0];
  if (!gp) return [0,0,0,0];

  // Xbox/standard mapping:
  // axes[0]=LX, axes[1]=LY, axes[2]=RX, axes[3]=RY
  const lx = gp.axes[0];
  const ly = gp.axes[1];
  const rx = gp.axes[2];
  const ry = gp.axes[3];

  const x = dz(-ry);   // forward/back (invert so up on stick = +forward)
  const y = dz( rx);   // left/right
  const z = dz(-ly);   // up/down (invert so up on stick = +up)
  const r = dz( lx);   // yaw

  // Convert to wire format expected by bridge: int16 roll, pitch, yaw, throttle, uint16 flags
  // Convention: roll = left/right, pitch = forward/back, throttle = up/down
    y = toInt16Norm(y);
    x = toInt16Norm(x);
    r = toInt16Norm(r);
    z = toInt16Norm(z);

  return [x,y,z,r];
}
