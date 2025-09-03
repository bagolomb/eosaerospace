<script>
  import { SvelteSet } from 'svelte/reactivity';

  let pressed = new SvelteSet(); // ✅ reactive Set
  let is_mac = $state(false);

  const mac_keys = [
    [
      {code:"Backquote", label:"`", width:1},
      {code:"Digit1", label:"1", width:1},
      {code:"Digit2", label:"2", width:1},
      {code:"Digit3", label:"3", width:1},
      {code:"Digit4", label:"4", width:1},
      {code:"Digit5", label:"5", width:1},
      {code:"Digit6", label:"6", width:1},
      {code:"Digit7", label:"7", width:1},
      {code:"Digit8", label:"8", width:1},
      {code:"Digit9", label:"9", width:1},
      {code:"Digit0", label:"0", width:1},
      {code:"Minus", label:"-", width:1},
      {code:"Equal", label:"=", width:1},
      {code:"Backspace", label:"delete", width:1.5}
    ],
    [
      {code:"Tab", label:"tab", width:1.5},
      {code:"KeyQ", label:"Q", width:1},
      {code:"KeyW", label:"W", width:1},
      {code:"KeyE", label:"E", width:1},
      {code:"KeyR", label:"R", width:1},
      {code:"KeyT", label:"T", width:1},
      {code:"KeyY", label:"Y", width:1},
      {code:"KeyU", label:"U", width:1},
      {code:"KeyI", label:"I", width:1},
      {code:"KeyO", label:"O", width:1},
      {code:"KeyP", label:"P", width:1},
      {code:"BracketLeft", label:"[", width:1},
      {code:"BracketRight", label:"]", width:1},
      {code:"Backslash", label:"\\", width:1}
    ],
    [
      {code:"CapsLock", label:"caps lock", width:1.75},
      {code:"KeyA", label:"A", width:1},
      {code:"KeyS", label:"S", width:1},
      {code:"KeyD", label:"D", width:1},
      {code:"KeyF", label:"F", width:1},
      {code:"KeyG", label:"G", width:1},
      {code:"KeyH", label:"H", width:1},
      {code:"KeyJ", label:"J", width:1},
      {code:"KeyK", label:"K", width:1},
      {code:"KeyL", label:"L", width:1},
      {code:"Semicolon", label:";", width:1},
      {code:"Quote", label:"'", width:1},
      {code:"Enter", label:"return", width:1.75}
    ],
    [
      {code:"ShiftLeft", label:"shift", width:2.25},
      {code:"KeyZ", label:"Z", width:1},
      {code:"KeyX", label:"X", width:1},
      {code:"KeyC", label:"C", width:1},
      {code:"KeyV", label:"V", width:1},
      {code:"KeyB", label:"B", width:1},
      {code:"KeyN", label:"N", width:1},
      {code:"KeyM", label:"M", width:1},
      {code:"Comma", label:",", width:1},
      {code:"Period", label:".", width:1},
      {code:"Slash", label:"/", width:1},
      {code:"ShiftRight", label:"shift", width:2.25}
    ],
    [
      {code:"Fn", label:"fn", width:1},
      {code:"ControlLeft", label:"control", width:1},
      {code:"AltLeft", label:"option", width:1},
      {code:"MetaLeft", label:"command", width:1.25},
      {code:"Space", label:"", width:5},
      {code:"MetaRight", label:"command", width:1.25},
      {code:"AltRight", label:"option", width:1},
      {code:"ArrowLeft", label:"\u2190", width:1},
      {code:"ArrowUp", label:"\u2191", width:1, stack: true},
      {code:"ArrowDown", label:"\u2193", width:1},
      {code:"ArrowRight", label:"\u2192", width:1}
    ],
  ];

  const windows_keys = [];

  const isPressed = (code) => pressed.has(code); // now reactive!

  function processRow(row) {
    const out = [];
    for (let i = 0; i < row.length; i++) {
      const k = row[i];
      if (k?.stack && row[i + 1]) {
        out.push({ type: "stack", top: k, bottom: row[i + 1], width: k.width ?? 1 });
        i++;
      } else {
        out.push({ type: "key", key: k });
      }
    }
    return out;
  }

  $effect(() => {
    is_mac = /Mac/.test(navigator.userAgent);
  });

  $effect(() => {
    const kd = (e) => pressed.add(e.code);
    const ku = (e) => pressed.delete(e.code);
    const blur = () => pressed.clear();

    window.addEventListener("keydown", kd);
    window.addEventListener("keyup", ku);
    window.addEventListener("blur", blur);

    return () => {
      window.removeEventListener("keydown", kd);
      window.removeEventListener("keyup", ku);
      window.removeEventListener("blur", blur);
    };
  });

  const baseKey =
    "relative rounded-md border border-zinc-300 dark:border-zinc-700 bg-zinc-100 dark:bg-zinc-800 text-xs md:text-sm flex items-center justify-center select-none min-w-0";
  const keyH = "h-full";
  const activeKey =
    "ring-2 ring-blue-500 border-blue-500 dark:ring-blue-400 dark:border-blue-400";
</script>



<!-- Give the keyboard a real height to flex into -->
<div class="bg-zinc-200 dark:bg-zinc-800 rounded-lg p-2 flex flex-col gap-1 h-full w-full min-h-0">
  {#each mac_keys as row}
    <!-- allow the row to shrink vertically -->
    <div class="flex gap-1 flex-1 items-stretch min-h-0">
      {#each processRow(row) as item}
        {#if item.type === "key"}
          <div
            class="{baseKey} {isPressed(item.key.code) ? activeKey : ''} h-full min-w-0 whitespace-nowrap overflow-hidden text-ellipsis"
            style="flex: {item.key.width ?? 1} 0 0"
            title={item.key.code}
          >
            {item.key.label}
          </div>
        {:else}
          <!-- stacked parent can shrink -->
          <div class="flex flex-col gap-0.5 flex-1 min-h-0 min-w-0" style="flex: {item.width} 0 0">
            <div class="{baseKey} {isPressed(item.top.code) ? activeKey : ''} flex-1 min-h-0"
                 title={item.top.code}>
              {item.top.label}
            </div>
            <div class="{baseKey} {isPressed(item.bottom.code) ? activeKey : ''} flex-1 min-h-0"
                 title={item.bottom.code}>
              {item.bottom.label}
            </div>
          </div>
        {/if}
      {/each}
    </div>
  {/each}
</div>