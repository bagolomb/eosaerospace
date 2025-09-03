<script>
	import { onMount } from 'svelte';
	import maplibregl from 'maplibre-gl';

	let map;
	let map_container;
	let draw;
	let currentMode = $state('select');
	let map_style = $state('vector');

	const API_KEY = import.meta.env.VITE_MAPTILER_KEY;

	const styles = {
		vector: `https://api.maptiler.com/maps/streets/style.json?key=${API_KEY}`,
		satellite: `https://api.maptiler.com/maps/hybrid/style.json?key=${API_KEY}`
	};

	$effect(() => {
		let style = styles[map_style]
		if (map && style) {
			map.setStyle(style);
		}
	});

	onMount(() => {
		map = new maplibregl.Map({
			container: map_container,
			style: styles[map_style],
			center: [-97.7431, 30.2672],
			zoom: 10,
			attributionControl: false
		});
	});

	function toggleStyle() {
		map_style = map_style === 'vector' ? 'satellite' : 'vector';
	}

</script>

<div class="relative w-full h-full">
  <!-- Map fills parent -->
  <div bind:this={map_container} class="absolute inset-0"></div>

  <!-- Pinned overlay control -->
  <button
    onclick={toggleStyle}
    class="absolute bottom-3 right-3 z-20 bg-blue-600 text-white px-3 py-2 rounded hover:bg-blue-700">
    Switch to {map_style === 'vector' ? 'Satellite' : 'Vector'}
  </button>
</div>