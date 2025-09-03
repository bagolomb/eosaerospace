<script>
	import { onMount } from "svelte"

	let buttons = $state([]);

	let gp_index = $state(0);
	let gp_connected = $state(false);
	let raf;
	const BTN = {
		A:0, B:1, X:2, Y:3, LB:4, RB:5, LT:6, RT:7,
		VIEW:8, MENU:9, LS:10, RS:11, DUP:12, DDOWN:13, DLEFT:14, DRIGHT:15
	}
	const AX = { LSX:0, LSY:1, RSX:2, RSY:3 }

	onMount(()=>{
		window.addEventListener("gamepadconnected", (e) => {
			gp_index = e.gamepad.index
			gp_connected = true
			loop()
		})
		window.addEventListener("gamepaddisconnected", () => {
			gp_connected = false
			cancelAnimationFrame(raf)
		})
		// if already plugged in before page load
		if (navigator.getGamepads) {
			const pads = navigator.getGamepads()
			for (let i = 0; i < pads.length; i++) if (pads[i]) {
				gp_index = pads[i].index; gp_connected = true; break
			}
			if (gp_connected) loop()
		}
	});
	function loop() {
		raf = requestAnimationFrame(loop)
		const gp = navigator.getGamepads?.()[gp_index]
		if (!gp) return
		updateFromGamepad(gp)
	}
	function press(id, pressed, analog=1) {
		const el = document.getElementById(id)
		if (!el) return
		// simple “lit when pressed” effect; scale for feedback
		el.style.filter = pressed ? "brightness(1.4)" : ""
		el.style.transform = pressed ? "scale(0.95)" : ""
		el.style.opacity = pressed ? String(0.6 + 0.4*analog) : ""
	}
	function stick(innerId, x, y) {
		const el = document.getElementById(innerId)
		if (!el) return
		// x,y in [-1,1]; move inner thumb within the big circle (≈30%)
		const pct = 100
		const tx = (x * pct).toFixed(1)
		const ty = (y * pct).toFixed(1)
		el.style.transform = `translate(-50%, -50%) translate(${tx}%, ${ty}%)`
	}
	function updateFromGamepad(gp) {
		// Buttons (digital/analog-safe)
		const b = gp.buttons
		press("a",  b[BTN.A]?.pressed,  b[BTN.A]?.value)
		press("b",  b[BTN.B]?.pressed,  b[BTN.B]?.value)
		press("x",  b[BTN.X]?.pressed,  b[BTN.X]?.value)
		press("y",  b[BTN.Y]?.pressed,  b[BTN.Y]?.value)

		press("lb", b[BTN.LB]?.pressed)
		press("rb", b[BTN.RB]?.pressed)

		press("view", b[BTN.VIEW]?.pressed)
		press("menu", b[BTN.MENU]?.pressed)

		// Triggers: show analog on bars lt/rt by opacity
		const lt = b[BTN.LT]?.value ?? 0
		const rt = b[BTN.RT]?.value ?? 0
		triggerFill("lt", lt)
		triggerFill("rt", rt)

		// D-pad
		press("du", b[BTN.DUP]?.pressed)
		press("dd", b[BTN.DDOWN]?.pressed)
		press("dl", b[BTN.DLEFT]?.pressed)
		press("dr", b[BTN.DRIGHT]?.pressed)

		// Sticks
		const ax = gp.axes
		stick("lsi", clamp(ax[AX.LSX]), clamp(ax[AX.LSY]))
		stick("rsi", clamp(ax[AX.RSX]), clamp(ax[AX.RSY]))

		// Stick-clicks? (optional)
		press("ls", b[BTN.LS]?.pressed)
		press("rs", b[BTN.RS]?.pressed)
	}

	function clamp(v) {
		if (typeof v !== "number") return 0
		// deadzone 0.08
		const dz = 0.08
		if (Math.abs(v) < dz) return 0
		return Math.max(-1, Math.min(1, v))
	}
	function triggerFill(id, value) {
		const v = Math.max(0, Math.min(1, value || 0))
		const fill = document.getElementById(id + "_fill")
		if (!fill) return
		// shrink the cover: 1 → 0 as you pull harder (shows travel)
		fill.style.transform = `scaleY(${1 - v})`
		// use the SAME visual as buttons (opacity/scale/brightness) based on analog v
		press(id, v > 0.05, v)   // at v=1 it fully “lights up” like your face buttons
	}
</script>

<div class="flex flex-col w-full h-full rounded-lg bg-zinc-150 dark:bg-zinc-800 items-center p-2">
	<div class="w-full h-1/3 flex flex-row gap-4 justify-center">
		<div class="w-1/3 h-full flex flex-col gap-4 justify-center">
			<!-- LT -->
			<div id="lt" class="w-full h-1/4 rounded-lg bg-zinc-300 dark:bg-zinc-700 relative overflow-hidden">
				<div id="lt_fill"
					class="absolute inset-0 origin-bottom bg-zinc-300 dark:bg-zinc-700"
					style="transform:scaleY(1);"></div>
			</div>
			<div id="lb" class="w-full h-1/4 rounded-lg bg-zinc-300 dark:bg-zinc-700"></div>
		</div>
		<div class="w-1/3 flex items-center gap-4 justify-center">
			<div id="view" class="w-1/4 h-1/4 rounded-full bg-zinc-300 dark:bg-zinc-700"></div>
			<div id="menu" class="w-1/4 h-1/4 rounded-full bg-zinc-300 dark:bg-zinc-700"></div>
		</div>
		<div class="w-1/3 h-full flex flex-col gap-4 justify-center">
			<!-- RT -->
			<div id="rt" class="w-full h-1/4 rounded-lg bg-zinc-300 dark:bg-zinc-700 relative overflow-hidden">
				<div id="rt_fill"
					class="absolute inset-0 origin-bottom bg-zinc-300 dark:bg-zinc-700"
					style="transform:scaleY(1);"></div>
			</div>
			<div id="rb" class="w-full h-1/4 rounded-lg bg-zinc-300 dark:bg-zinc-700"></div>
		</div>
	</div>
	<!-- bottom row -->
	<div class="w-full h-2/3 flex flex-row gap-4 justify-center">
		<!-- left joystick -->
		<div class="w-1/4 flex items-center justify-center">
			<div id="ls" class="h-full aspect-square rounded-full bg-zinc-300 dark:bg-zinc-700 relative overflow-hidden">
				<!-- Movable inner circle -->
				<div id="lsi"
					class="absolute top-1/2 left-1/2 w-1/3 aspect-square rounded-full bg-zinc-500 dark:bg-zinc-400 transition-transform duration-50" 
					style="transform: translate(-50%,-50%);"
				></div>
			</div>
		</div>

		<!-- D-pad -->
		<div class="w-1/4 flex items-center justify-center">
			<div class="grid grid-cols-3 grid-rows-3 gap-1 w-full h-full aspect-square">
				<!-- Row 1 -->
				<div></div>
				<div id="du" class="rounded-md bg-zinc-300 dark:bg-zinc-700"></div>
				<div></div>

				<!-- Row 2 -->
				<div id="dl" class="rounded-md bg-zinc-300 dark:bg-zinc-700"></div>
				<div></div>
				<div id="dr" class="rounded-md bg-zinc-300 dark:bg-zinc-700"></div>

				<!-- Row 3 -->
				<div></div>
				<div id="dd" class="rounded-md bg-zinc-300 dark:bg-zinc-700"></div>
				<div></div>
			</div>
		</div>

		<!-- buttons -->
		<div class="w-1/4 flex items-center justify-center">
			<div class="grid grid-cols-3 grid-rows-3 h-full w-full gap-1 aspect-square">
				<div></div>
				<div id="y" class="h-full rounded-full bg-amber-400 dark:bg-amber-600"></div>
				<div></div>
				<div id="x" class="h-full rounded-full bg-sky-400 dark:bg-sky-600"></div>
				<div></div>
				<div id="b" class="h-full rounded-full bg-rose-400 dark:bg-rose-600"></div>
				<div></div>
				<div id="a" class="h-full rounded-full bg-emerald-400 dark:bg-emerald-600"></div>
				<div></div>
			</div>
		</div>

		<!-- right joystick -->
		<div class="w-1/4 flex items-center justify-center">
			<div id="rs" class="h-full aspect-square rounded-full bg-zinc-300 dark:bg-zinc-700 relative overflow-hidden">
				<!-- Movable inner circle -->
				<div id="rsi"
					class="absolute top-1/2 left-1/2 w-1/3 aspect-square rounded-full bg-zinc-500 dark:bg-zinc-400 transition-transform duration-50" 
					style="transform: translate(-50%,-50%);"
				></div>
			</div>
		</div>
	</div>
</div>