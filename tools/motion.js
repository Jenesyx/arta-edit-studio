/* Arta Edit Studio — motion library.
 *
 * Loaded into every composition after GSAP + MotionPathPlugin + CustomEase and
 * before the timeline script. Every helper adds tweens to the global paused
 * timeline `tl` at ABSOLUTE times, so everything stays seekable / deterministic.
 * Full guide: docs/motion.md
 *
 *   arcIn(sel, t, {from:[dx,dy], bend, dur, blur})   enter along a curve (+ motion blur)
 *   arcOut(sel, t, {to:[dx,dy], bend, dur, blur})    leave along a curve
 *   whip(sel, t, {from:"right"|"left"|"up"|"down"})   full-frame whip with directional blur
 *   mblur(sel, t, dur, "x"|"y", amount)               directional motion blur ramp
 *   settle(sel, t, {from, dur})                        slam in, overshoot, settle (big words)
 *   kf(sel, t, frames)                                 GSAP keyframes, smooth eases by default
 *   floaty(sel, t, dur, amp)                           idle secondary motion (after the entrance)
 *   camTo(t, {scale, x, y, rotation, dur})             camera move on #cam (story layout)
 */

gsap.registerPlugin(MotionPathPlugin, CustomEase);

// House curves. "studio" = fast start, long soft landing: the default for anything arriving.
CustomEase.create("studio", "M0,0 C0.16,1 0.3,1 1,1");
CustomEase.create("studioIn", "M0,0 C0.7,0 0.84,0 1,1");          // leaving: accelerate away
CustomEase.create("studioInOut", "M0,0 C0.65,0 0.35,1 1,1");      // position / camera moves

const EASE = { enter: "studio", exit: "studioIn", move: "studioInOut", pop: "back.out(1.6)",
               cam: "studioInOut", float: "sine.inOut", snap: "expo.out" };
const DUR = { enter: 0.5, exit: 0.24, move: 0.6, pop: 0.38, cam: 0.8 };
const STAGGER = 0.06;

const __NS = "http://www.w3.org/2000/svg";
let __mbSvg = null, __mbN = 0;

function __els(sel) {
  if (typeof sel !== "string") return [].concat(sel);
  return Array.from(document.querySelectorAll(sel));
}

// One feGaussianBlur per element; stdDeviation "N 0" blurs along x only -> real directional blur.
// The filter region only grows along the blur axis, by what the blur needs (3 sigma): a
// full-frame wrapper with a generous region costs a 2-4x frame-sized buffer per frame.
function __blur(el, axis, amount) {
  if (el.__mb) return el.__mb;
  if (!__mbSvg) {
    __mbSvg = document.createElementNS(__NS, "svg");
    __mbSvg.setAttribute("width", "0"); __mbSvg.setAttribute("height", "0");
    __mbSvg.style.cssText = "position:absolute;width:0;height:0;overflow:hidden";
    document.body.appendChild(__mbSvg);
  }
  const id = "mb" + (++__mbN);
  const f = document.createElementNS(__NS, "filter");
  f.setAttribute("id", id);
  const w = el.offsetWidth || 400, h = el.offsetHeight || 200;
  const mx = axis === "y" ? 0.02 : Math.min(0.6, (3 * amount) / w);
  const my = axis === "y" ? Math.min(0.6, (3 * amount) / h) : 0.02;
  f.setAttribute("x", `${-mx * 100}%`); f.setAttribute("y", `${-my * 100}%`);
  f.setAttribute("width", `${(1 + 2 * mx) * 100}%`); f.setAttribute("height", `${(1 + 2 * my) * 100}%`);
  f.setAttribute("color-interpolation-filters", "sRGB");
  const g = document.createElementNS(__NS, "feGaussianBlur");
  g.setAttribute("stdDeviation", "0 0");
  f.appendChild(g); __mbSvg.appendChild(f);
  const base = getComputedStyle(el).filter;
  el.__mb = { g, id, base: base && base !== "none" ? base : "" };
  return el.__mb;
}

// Blur ramps up to `amount` px at 35 % of the move, back to 0 at the end. The filter
// is only attached during the move so resting text stays perfectly sharp.
function mblur(sel, t, d, axis, amount) {
  amount = amount || 16;
  __els(sel).forEach((el) => {
    const b = __blur(el, axis, amount);
    const v = (a) => (axis === "y" ? `0 ${a}` : `${a} 0`);
    tl.set(el, { filter: `${b.base} url(#${b.id})`.trim() }, t);
    tl.fromTo(b.g, { attr: { stdDeviation: v(0) } },
      { attr: { stdDeviation: v(amount) }, duration: d * 0.35, ease: "power1.in", immediateRender: false }, t);
    tl.to(b.g, { attr: { stdDeviation: v(0) }, duration: d * 0.65, ease: "power2.out" }, t + d * 0.35);
    tl.set(el, { filter: b.base || "none" }, t + d);
  });
}

// Three points from (dx,dy) to (0,0), the middle one pushed sideways by `bend`
// (fraction of the distance) -> a gentle arc instead of a straight slide.
function __arc(dx, dy, bend) {
  return [{ x: dx, y: dy }, { x: dx / 2 - dy * bend, y: dy / 2 + dx * bend }, { x: 0, y: 0 }];
}

function arcIn(sel, t, o) {
  o = Object.assign({ from: [0, 320], bend: 0.22, dur: DUR.enter, ease: EASE.enter, blur: 14, rot: 0 }, o || {});
  const [dx, dy] = o.from;
  gsap.set(sel, { x: dx, y: dy, autoAlpha: 0, rotation: o.rot });
  tl.to(sel, { motionPath: { path: __arc(dx, dy, o.bend), curviness: 1.25, fromCurrent: false },
               autoAlpha: 1, rotation: 0, duration: o.dur, ease: o.ease }, t);
  if (o.blur) mblur(sel, t, o.dur * 0.7, Math.abs(dx) >= Math.abs(dy) ? "x" : "y", o.blur);
}

function arcOut(sel, t, o) {
  o = Object.assign({ to: [0, -320], bend: -0.22, dur: DUR.exit, ease: EASE.exit, blur: 14 }, o || {});
  const [dx, dy] = o.to;
  tl.to(sel, { motionPath: { path: __arc(dx, dy, o.bend).reverse(), curviness: 1.25, fromCurrent: false },
               autoAlpha: 0, duration: o.dur, ease: o.ease }, t);
  if (o.blur) mblur(sel, t + o.dur * 0.25, o.dur * 0.75, Math.abs(dx) >= Math.abs(dy) ? "x" : "y", o.blur);
}

function whip(sel, t, o) {
  o = Object.assign({ from: "right", dur: 0.34, blur: 30 }, o || {});
  const d = { right: [1080, 0], left: [-1080, 0], up: [0, -1920], down: [0, 1920] }[o.from];
  tl.fromTo(sel, { x: d[0], y: d[1] }, { x: 0, y: 0, duration: o.dur, ease: EASE.snap }, t);
  mblur(sel, t, o.dur, d[0] ? "x" : "y", o.blur);
}

function settle(sel, t, o) {
  o = Object.assign({ from: 1.6, dur: 0.6 }, o || {});
  gsap.set(sel, { scale: o.from, autoAlpha: 0 });
  tl.to(sel, { keyframes: [
    { scale: 0.95, autoAlpha: 1, duration: o.dur * 0.42, ease: "power3.in" },
    { scale: 1.03, duration: o.dur * 0.3, ease: "sine.out" },
    { scale: 1, duration: o.dur * 0.28, ease: "sine.inOut" }] }, t);
}

function kf(sel, t, frames) {
  tl.to(sel, { keyframes: frames.map((f) => Object.assign({ ease: EASE.move }, f)) }, t);
}

function floaty(sel, t, dur, amp) {
  amp = amp || 10;
  const reps = Math.max(1, Math.floor(dur / 1.4)) | 1;   // odd -> ends where it started
  tl.fromTo(sel, { y: 0 }, { y: -amp, duration: 1.4, ease: EASE.float, yoyo: true, repeat: reps,
                             immediateRender: false }, t);
}

function camTo(t, o) {
  o = Object.assign({ dur: DUR.cam, ease: EASE.cam }, o || {});
  const v = {};
  for (const k of ["scale", "x", "y", "rotation"]) if (k in o) v[k] = o[k];
  tl.to("#cam", Object.assign(v, { duration: o.dur, ease: o.ease }), t);
}
