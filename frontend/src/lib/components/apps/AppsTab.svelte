<script>
  import IconApps from '@material-symbols/svg-400/rounded/apps-fill.svg?component';
  import { toaster } from '@/lib/toast';

  /** @type {{ apiBase?: string }} */
  let { apiBase = '' } = $props();

  const PLACEHOLDER_APPS = [
    { app: 'rinkhals-webui', name: 'Rinkhals WebUI', description: 'Web-based administration UI.', version: '1.0.0', enabled: true, status: 'running' },
    { app: 'moonraker-api', name: 'Moonraker API', description: 'Moonraker REST API for Rinkhals.', version: '0.9.3', enabled: true, status: 'running' },
    { app: 'fluidd', name: 'Fluidd', description: 'Fluidd web interface for Klipper.', version: '1.31.0', enabled: false, status: 'stopped' },
  ];

  /** @type {typeof PLACEHOLDER_APPS} */
  let apps = $state(PLACEHOLDER_APPS);
  let loading = $state(false);
  /** @type {Set<string>} */
  let togglingApps = $state(new Set());

  $effect(() => {
    fetchApps();
  });

  async function fetchApps() {
    loading = true;
    try {
      const res = await fetch(`${apiBase}/api/apps`);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      apps = data.apps ?? [];
    } catch (err) {
      if (apps === PLACEHOLDER_APPS) toaster.error({ title: 'Apps', description: String(err) });
    } finally {
      loading = false;
    }
  }

  /** @param {string} appName */
  async function toggleApp(appName) {
    togglingApps = new Set([...togglingApps, appName]);
    try {
      const res = await fetch(`${apiBase}/api/apps/${encodeURIComponent(appName)}/toggle`, {
        method: 'POST',
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      apps = apps.map(a => (a.app === appName ? { ...a, enabled: data.enabled } : a));
    } catch (err) {
      toaster.error({ title: 'Toggle app', description: String(err) });
    } finally {
      togglingApps = new Set([...togglingApps].filter(n => n !== appName));
    }
  }
</script>

<div class="max-w-xl mx-auto flex flex-col gap-3">
  {#if loading && apps === PLACEHOLDER_APPS}
    <div class="flex justify-center py-16">
      <span class="loading loading-spinner loading-lg"></span>
    </div>
  {:else if apps.length === 0}
    <div class="card card-border">
      <div class="card-body items-center text-center py-16">
        <IconApps width={40} height={40} fill="currentColor" class="opacity-30" />
        <p class="text-base-content/60 text-sm mt-3">No apps installed</p>
      </div>
    </div>
  {:else}
    {#each apps as app (app.app)}
      <div class="card card-border">
        <div class="card-body gap-2 py-4">
          <div class="flex items-start justify-between gap-3">
            <!-- App metadata -->
            <div class="flex-1 min-w-0">
              <div class="flex items-center gap-2 flex-wrap">
                <span class="font-semibold truncate">{app.name}</span>
                {#if app.version}
                  <span class="badge badge-ghost badge-sm shrink-0">v{app.version}</span>
                {/if}
                <span
                  class="badge badge-sm shrink-0 {app.status === 'running'
                    ? 'badge-success'
                    : 'badge-neutral'}"
                >
                  {app.status}
                </span>
              </div>
              {#if app.description}
                <p class="text-sm text-base-content/70 mt-1">{app.description}</p>
              {/if}
            </div>

            <!-- Enable/disable toggle -->
            <label class="flex items-center shrink-0 cursor-pointer" title="{app.enabled ? 'Disable' : 'Enable'} {app.name}">
              {#if togglingApps.has(app.app)}
                <span class="loading loading-spinner loading-sm"></span>
              {:else}
                <input
                  type="checkbox"
                  class="toggle toggle-primary"
                  checked={app.enabled}
                  onchange={() => toggleApp(app.app)}
                />
              {/if}
            </label>
          </div>
        </div>
      </div>
    {/each}
  {/if}
</div>
