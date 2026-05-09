<script>
  import FilamentHub from './lib/components/FilamentHub.svelte';
  import ThemeToggle from './lib/components/ThemeToggle.svelte';
</script>

<div class="navbar bg-base-200">
  <div class="flex-1">
    <span class="font-bold text-lg px-2">Rinkhals WebUI</span>
  </div>
  <div class="flex-none pr-2">
    <ThemeToggle />
  </div>
</div>
<main class="p-6">
  <section>
    <FilamentHub aceId={0} />
  </section>
</main>
