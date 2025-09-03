<script>
	import '../app.css';
	
	let { children } = $props();
</script>

<div class="w-screen h-screen flex flex-col items-center bg-zinc-100 dark:bg-zinc-900 text-zinc-900 dark:text-zinc-100">
	{@render children?.()}
</div>

