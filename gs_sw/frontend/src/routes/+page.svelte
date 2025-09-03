<script>
    import "$lib/funcs/controller.js";
    import CommandPanel from "$lib/components/CommandPanel.svelte";
    import Controller from "$lib/components/Controller.svelte";
    import Keyboard from "$lib/components/Keyboard.svelte";
    import Map from "$lib/components/Map.svelte"
    import { PaneGroup, Pane, PaneResizer } from "paneforge";
    import Button from "$lib/components/ui/Button.svelte";

    let controller_tab_state = $state("keyboard");
</script>

<PaneGroup direction="horizontal" class="w-full h-full">
	<Pane defaultSize={20}>
        <CommandPanel></CommandPanel>
    </Pane>
	<PaneResizer class="w-2 bg-zinc-50 dark:bg-zinc-950"/>
	<Pane defaultSize={80}>
        <PaneGroup direction="vertical" class="w-full h-full">
            <Pane defaultSize={70}>
                <Map>
                </Map>
            </Pane>
            <PaneResizer class="h-2 bg-zinc-50 dark:bg-zinc-950"/>
            <Pane defaultSize={30} class="flex w-full h-full">
                <div class="w-full h-full flex flex-row">
                    <div class="flex flex-col justify-evenly pl-2">
                        <Button onclick={() => controller_tab_state = "keyboard"} class={controller_tab_state === "keyboard" ? "border" : "border border-transparent"}>Keyboard</Button>
                        <Button onclick={() => controller_tab_state = "controller"} class={controller_tab_state === "controller" ? "border" : "border border-transparent"}>Controller</Button>
                    </div>
                    <div class="w-full h-full flex p-2">
                        {#if controller_tab_state==="keyboard"}
                            <Keyboard></Keyboard>
                        {:else if controller_tab_state==="controller"}
                            <Controller></Controller>
                        {/if}
                    </div>
                </div>
            </Pane>
        </PaneGroup>
    </Pane>
</PaneGroup>

