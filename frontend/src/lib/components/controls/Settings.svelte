<script>
  import IconRefresh from '@material-symbols/svg-400/rounded/refresh-fill.svg?component';
  import IconAutorenew from '@material-symbols/svg-400/rounded/autorenew-fill.svg?component';
  import IconLightbulb from '@material-symbols/svg-400/rounded/lightbulb-fill.svg?component';
  import IconVideocam from '@material-symbols/svg-400/rounded/videocam-fill.svg?component';
  import { toaster } from '@/lib/toast';

  /**
   * @type {{
   *   apiBase?: string,
   *   onRefresh?: () => void,
   * }}
   */
  let { apiBase = '', onRefresh } = $props();

  let autoRefill = $state(false);
  let configLoading = $state(false);

  let ledOn = $state(false);
  let ledLoading = $state(false);

  let cameraLedOn = $state(false);
  let cameraLedLoading = $state(false);

  $effect(() => {
    fetch(`${apiBase}/api/camera-led`)
      .then(r => r.ok ? r.json() : Promise.reject(`HTTP ${r.status}`))
      .then(d => { cameraLedOn = Boolean(d.on); })
      .catch(() => {}); // non-fatal — camera may not be present
  });

  async function handleCameraLedChange(e) {
    const newVal = e.target.checked;
    cameraLedLoading = true;
    try {
      const res = await fetch(`${apiBase}/api/camera-led`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ on: newVal }),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      cameraLedOn = newVal;
    } catch (err) {
      toaster.error({ title: 'Camera LED', description: String(err) });
      cameraLedOn = !newVal; // revert
    } finally {
      cameraLedLoading = false;
    }
  }

  async function handleLedChange(e) {
    const newVal = e.target.checked;
    ledLoading = true;
    try {
      const res = await fetch(`${apiBase}/api/led`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ on: newVal }),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      ledOn = newVal;
    } catch (err) {
      toaster.error({ title: 'Print head LED', description: String(err) });
      ledOn = !newVal; // revert
    } finally {
      ledLoading = false;
    }
  }

  $effect(() => {
    fetchConfig();
  });

  async function fetchConfig() {
    try {
      const res = await fetch(`${apiBase}/api/ace/config`);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      autoRefill = Boolean(data.auto_refill);
    } catch (err) {
      toaster.error({ title: 'Settings', description: String(err) });
    }
  }

  async function handleAutoRefillChange(e) {
    const newVal = e.target.checked;
    configLoading = true;
    try {
      const res = await fetch(`${apiBase}/api/ace/config`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ auto_refill: newVal ? 1 : 0 }),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      autoRefill = newVal;
    } catch (err) {
      toaster.error({ title: 'Filament auto-refill', description: String(err) });
      autoRefill = !newVal; // revert optimistic toggle
    } finally {
      configLoading = false;
    }
  }

  async function handleRefresh() {
    await fetchConfig();
    onRefresh?.();
  }
</script>

<div class="card card-border bg-base-100 border-base-300">
  <div class="card-body gap-3">
    <h2 class="card-title text-base">Settings</h2>

    <div class="flex flex-wrap items-center gap-3">
      <button type="button" class="btn btn-sm btn-neutral" onclick={handleRefresh}>
        <IconRefresh class="icon-inline" />
        Refresh ACE status
      </button>

      <label class="flex items-center gap-2 cursor-pointer select-none">
        <span class="text-sm flex items-center gap-1.5">
          <IconAutorenew class="icon-inline" />
          Filament auto-refill
        </span>
        <input
          type="checkbox"
          class="toggle toggle-primary toggle-sm"
          checked={autoRefill}
          disabled={configLoading}
          onchange={handleAutoRefillChange}
        />
      </label>

      <label class="flex items-center gap-2 cursor-pointer select-none">
        <span class="text-sm flex items-center gap-1.5">
          <IconLightbulb class="icon-inline" />
          Print head LED
        </span>
        <input
          type="checkbox"
          class="toggle toggle-primary toggle-sm"
          checked={ledOn}
          disabled={ledLoading}
          onchange={handleLedChange}
        />
      </label>

      <label class="flex items-center gap-2 cursor-pointer select-none">
        <span class="text-sm flex items-center gap-1.5">
          <IconVideocam class="icon-inline" />
          Camera LED
        </span>
        <input
          type="checkbox"
          class="toggle toggle-primary toggle-sm"
          checked={cameraLedOn}
          disabled={cameraLedLoading}
          onchange={handleCameraLedChange}
        />
      </label>
    </div>

  </div>
</div>
