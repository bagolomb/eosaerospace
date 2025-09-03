<script>
    let { children, onclick={} , class:className = "" } = $props()
</script>

<button class="flex p-2 rounded-lg 
	bg-zinc-300 hover:bg-zinc-400 active:bg-zinc-500
	dark:bg-zinc-700 dark:hover:bg-zinc-600 dark:active:bg-zinc-500
	{className}" onclick={onclick}>
    {@render children?.()}
</button>