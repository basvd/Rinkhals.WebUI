<script>
  import Navbar from './lib/components/Navbar.svelte';
  import Toaster from './lib/components/Toaster.svelte';
  import ControlsTab from './lib/components/controls/ControlsTab.svelte';
  import AppsTab from './lib/components/apps/AppsTab.svelte';
  import SystemTab from './lib/components/system/SystemTab.svelte';

  const apiBase = '';

  /** @type {'controls' | 'apps' | 'system'} */
  let activeTab = $state('controls');
</script>

<div class="flex flex-col h-dvh">
  <Navbar {activeTab} onTabChange={(tab) => (activeTab = tab)} />

  <main class="flex-1 overflow-y-auto p-4 sm:p-6 bg-base-200">
    {#if activeTab === 'controls'}
      <ControlsTab {apiBase} />
    {:else if activeTab === 'apps'}
      <AppsTab {apiBase} />
    {:else if activeTab === 'system'}
      <SystemTab {apiBase} />
    {/if}
  </main>

  <Toaster />
</div>

