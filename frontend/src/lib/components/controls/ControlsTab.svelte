<script>
  import Settings from './Settings.svelte';
  import FilamentHub from './FilamentHub.svelte';

  /** @type {{ apiBase?: string }} */
  let { apiBase = '' } = $props();

  let refreshTick = $state(0);
</script>

<div class="flex flex-col gap-4 max-w-xl mx-auto">
  <Settings {apiBase} onRefresh={() => refreshTick++} />
  <FilamentHub aceId={0} {apiBase} {refreshTick} />
</div>
