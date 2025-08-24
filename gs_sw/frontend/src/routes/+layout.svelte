<script>
	import '../app.css';
	import favicon from '$lib/assets/favicon.svg';
	
	let { children } = $props();
</script>

<div class="w-full h-full flex flex-col items-center bg-zinc-100 dark:bg-zinc-900 text-zinc-900 dark:text-zinc-100">
	{@render children?.()}
</div>

