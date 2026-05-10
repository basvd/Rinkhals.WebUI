<script>
  import ConfirmDialog from '../ConfirmDialog.svelte';
  import IconArticle from '@material-symbols/svg-400/rounded/article-fill.svg?component';
  import IconSync from '@material-symbols/svg-400/rounded/sync-fill.svg?component';
  import IconRestart from '@material-symbols/svg-400/rounded/restart_alt-fill.svg?component';
  import IconUpdate from '@material-symbols/svg-400/rounded/system_update_alt-fill.svg?component';
  import IconCheckCircle from '@material-symbols/svg-400/rounded/check_circle-fill.svg?component';
  import IconDownload from '@material-symbols/svg-400/rounded/download-fill.svg?component';
  import IconWarning from '@material-symbols/svg-400/rounded/warning-fill.svg?component';
  import { toaster } from '@/lib/toast';

  /** @type {{ apiBase?: string }} */
  let { apiBase = '' } = $props();

  // ── Logs ─────────────────────────────────────────────────────────────────
  let logsVisible = $state(false);
  let logsContent = $state('');
  let logsLoading = $state(false);

  async function toggleLogs() {
    if (logsVisible) {
      logsVisible = false;
      return;
    }
    logsLoading = true;
    try {
      const res = await fetch(`${apiBase}/api/system/logs`);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      logsContent = await res.text();
      logsVisible = true;
    } catch (err) {
      toaster.error({ title: 'Logs', description: String(err) });
    } finally {
      logsLoading = false;
    }
  }

  // ── Sync ─────────────────────────────────────────────────────────────────
  let syncLoading = $state(false);

  async function handleSync() {
    syncLoading = true;
    try {
      const res = await fetch(`${apiBase}/api/system/sync`, { method: 'POST' });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      toaster.success({ title: 'Filesystem synced' });
    } catch (err) {
      toaster.error({ title: 'Sync', description: String(err) });
    } finally {
      syncLoading = false;
    }
  }

  // ── Reboot ────────────────────────────────────────────────────────────────
  /** @type {import('../ConfirmDialog.svelte').default} */
  let rebootDialog;
  let rebootLoading = $state(false);

  async function handleReboot() {
    rebootLoading = true;
    try {
      await fetch(`${apiBase}/api/system/reboot`, { method: 'POST' });
    } catch {
      // Expected — connection drops when the printer reboots
    } finally {
      rebootDialog.close();
      rebootLoading = false;
    }
  }

  // ── Firmware Update ───────────────────────────────────────────────────────
  let updateLoading = $state(false);
  /** @type {Record<string,any>|null} */
  let updateInfo = $state(null);

  async function checkUpdate() {
    updateLoading = true;
    updateInfo = null;
    try {
      const res = await fetch(`${apiBase}/api/system/update`);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      updateInfo = await res.json();
    } catch (err) {
      toaster.error({ title: 'Update check', description: String(err) });
    } finally {
      updateLoading = false;
    }
  }
</script>

<div class="max-w-xl mx-auto flex flex-col gap-4">

  <!-- ── Rinkhals section ─────────────────────────────────────────────── -->
  <div class="card card-border">
    <div class="card-body gap-3">
      <h2 class="card-title text-base">Rinkhals</h2>

      <div class="flex flex-wrap gap-3">
        <button
          type="button"
          class="btn btn-sm btn-neutral"
          disabled={logsLoading}
          onclick={toggleLogs}
        >
          {#if logsLoading}
            <span class="loading loading-spinner loading-xs"></span>
          {:else}
            <IconArticle class="icon-inline" />
          {/if}
          {logsVisible ? 'Hide logs' : 'Show logs'}
        </button>
      </div>

      {#if logsVisible}
        <pre
          class="bg-base-300 rounded-box p-3 text-xs font-mono leading-relaxed overflow-x-auto overflow-y-auto max-h-72 whitespace-pre-wrap break-all"
        >{logsContent || '(empty)'}</pre>
      {/if}
    </div>
  </div>

  <!-- ── Printer section ──────────────────────────────────────────────── -->
  <div class="card card-border">
    <div class="card-body gap-3">
      <h2 class="card-title text-base">Printer</h2>

      <div class="flex flex-wrap gap-3">
        <button
          type="button"
          class="btn btn-sm btn-neutral"
          disabled={syncLoading}
          onclick={handleSync}
        >
          {#if syncLoading}
            <span class="loading loading-spinner loading-xs"></span>
          {:else}
            <IconSync class="icon-inline" />
          {/if}
          Sync filesystem
        </button>

        <button
          type="button"
          class="btn btn-sm btn-error btn-outline"
          onclick={() => rebootDialog.open()}
        >
          <IconRestart class="icon-inline" />
          Reboot
        </button>
      </div>
    </div>
  </div>

  <!-- ── Firmware Update section ──────────────────────────────────────── -->
  <div class="card card-border">
    <div class="card-body gap-3">
      <h2 class="card-title text-base">Firmware Update</h2>

      <div class="flex flex-wrap gap-3">
        <button
          type="button"
          class="btn btn-sm btn-neutral"
          disabled={updateLoading}
          onclick={checkUpdate}
        >
          {#if updateLoading}
            <span class="loading loading-spinner loading-xs"></span>
          {:else}
            <IconUpdate class="icon-inline" />
          {/if}
          Check for update
        </button>
      </div>

      {#if updateInfo}
        {#if updateInfo.status === 'timed_out'}
          <div role="alert" class="alert alert-warning text-sm">
            <IconWarning class="icon-inline" />
            Update check timed out — try again later.
          </div>
        {:else if updateInfo.status === 'error'}
          <div role="alert" class="alert alert-error text-sm">
            {updateInfo.message ?? 'Update check failed'}
          </div>
        {:else if updateInfo.status === 'up_to_date'}
          <div role="alert" class="alert alert-success text-sm">
            <IconCheckCircle class="icon-inline" />
            Firmware is up to date{#if updateInfo.version}&nbsp;(v{updateInfo.version}){/if}
          </div>
        {:else}
          <!-- update_available or any version present -->
          <div class="rounded-box border border-info/30 bg-info/10 p-3 text-sm space-y-1">
            <p class="flex items-center gap-2 font-semibold text-info">
              <IconDownload class="icon-inline" />
              Update available{#if updateInfo.version}&nbsp;— v{updateInfo.version}{/if}
            </p>
            {#if updateInfo.release_date}
              <p class="text-base-content/70">Released: {updateInfo.release_date}</p>
            {/if}
            {#if updateInfo.size_mb}
              <p class="text-base-content/70">Size: {updateInfo.size_mb} MB</p>
            {/if}
            {#if updateInfo.description}
              <p class="text-base-content/70 mt-2">{updateInfo.description}</p>
            {/if}
            <p class="text-base-content/50 text-xs mt-2">
              Install via USB drive — see documentation.
            </p>
          </div>
        {/if}
      {/if}
    </div>
  </div>
</div>

<!-- Reboot confirmation dialog -->
<ConfirmDialog
  bind:this={rebootDialog}
  title="Reboot printer?"
  message="The printer will reboot immediately. Any active print will be interrupted."
  confirmLabel="Reboot now"
  confirmClass="btn-error"
  loading={rebootLoading}
  onConfirm={handleReboot}
/>
