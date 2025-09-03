<script>
    import Button from "./ui/Button.svelte";
    import { getRCInput } from "$lib/funcs/controller.js"
    import { rc_control } from "$lib/state.svelte.js";
    import { sendCmd, sendRC } from "$lib/funcs/ws.js"

    let intervalId;

    $effect(() => {
		if (rc_control.rc_control) {
			console.log("🟢 RC Control started");
			intervalId = setInterval(() => {
				const [x, y, z, r] = getRCInput();
				sendRC(x, y, z, r);
			}, 20); // 50Hz
		} else {
			console.log("🔴 RC Control stopped");
			clearInterval(intervalId);
		}

		// Cleanup if rc_control changes or component unmounts
		return () => clearInterval(intervalId);
	});
</script>

<div class="w-full h-full p-2 flex flex-col items-center">
    <h1>
        Command Panel
    </h1>
    <div class="w-full p-2 flex flex-row justify-evenly">
        <Button onclick={() => {sendCmd("arm")}}>
            Arm
        </Button>
        <Button onclick={() => {sendCmd("disarm")}}>
            Disarm
        </Button>
    </div>
    <div class="w-full p-2 flex flex-row justify-evenly">
        <Button onclick={() => {sendCmd("takeoff")}}>
            Takeoff
        </Button>
        <Button onclick={() => {sendCmd("land")}}>
            Land
        </Button>
    </div>
    <div class="w-full p-2 flex flex-row justify-evenly">
        <Button onclick={() => {
                sendCmd("offboard_start");
                rc_control.rc_control = true;
            }}>
            Start RC
        </Button>
        <Button onclick={() => {
                sendCmd("offboard_stop");
                rc_control.rc_control = false;
            }}>
            End RC
        </Button>
    </div>
</div>