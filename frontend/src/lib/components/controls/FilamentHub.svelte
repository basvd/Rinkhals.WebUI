<script>
  import IconCounter1 from '@material-symbols/svg-400/rounded/counter_1-fill.svg?component';
  import IconCounter2 from '@material-symbols/svg-400/rounded/counter_2-fill.svg?component';
  import IconCounter3 from '@material-symbols/svg-400/rounded/counter_3-fill.svg?component';
  import IconCounter4 from '@material-symbols/svg-400/rounded/counter_4-fill.svg?component';
  import IconHeat from '@material-symbols/svg-400/rounded/heat-fill.svg?component';
  import IconStop from '@material-symbols/svg-400/rounded/stop-fill.svg?component';
  import IconThermostat from '@material-symbols/svg-400/rounded/device_thermostat-fill.svg?component';
  import IconTimer from '@material-symbols/svg-400/rounded/timer-fill.svg?component';
  import FilamentSlotDialog from './FilamentSlotDialog.svelte';
  import { toaster } from '@/lib/toast';

  const SLOT_ICONS = [IconCounter1, IconCounter2, IconCounter3, IconCounter4];

  /**
   * @type {{
   *   aceId?: number,
   *   apiBase?: string,
   *   refreshTick?: number
   * }}
   */
  let { aceId = 0, apiBase = '', refreshTick = 0 } = $props();

  // Re-fetch whenever refreshTick changes (also runs on mount)
  $effect(() => {
    void refreshTick;
    fetchHub();
  });

  /* ------------------------------------------------------------------ */
  /*  Placeholder data (used until the backend is available)             */
  /* ------------------------------------------------------------------ */

  const PLACEHOLDER_HUB = {
    id: 0,
    status: 'ready',
    temperature: 27,
    slots: [
      { index: 0, status: 'loaded', type: 'PLA',  color: { rgb: { r: 255, g: 50, b: 50 },  hex: '#FF3232' } },
      { index: 1, status: 'loaded', type: 'PETG', color: { rgb: { r: 50, g: 180, b: 255 }, hex: '#32B4FF' } },
      { index: 2, status: 'loaded', type: 'ABS',  color: { rgb: { r: 60, g: 60, b: 60 },   hex: '#3C3C3C' } },
      { index: 3, status: 'empty',  type: null,    color: null },
    ],
    dryer: {
      status: 'stop',
      target_temp: null,
      remaining_seconds: null,
      is_active: false,
    },
  };

  /* ------------------------------------------------------------------ */
  /*  Hub state                                                          */
  /* ------------------------------------------------------------------ */

  /** @type {{ id: number, status: string|null, temperature: number|null,
   *           slots: Array<{ index: number, status: string|null, type: string|null,
   *                          color: { rgb: {r:number,g:number,b:number}, hex: string }|null }>,
   *           dryer: { status: string|null, target_temp: number|null,
   *                    remaining_seconds: number|null, is_active: boolean } }|null} */
  let hub = $state(PLACEHOLDER_HUB);
  let loading = $state(false);

  /* ------------------------------------------------------------------ */
  /*  Drying controls                                                    */
  /* ------------------------------------------------------------------ */

  let dryTemp = $state(50);
  let dryDuration = $state(4);       // hours
  let dryLoading = $state(false);

  /* ------------------------------------------------------------------ */
  /*  Slot‑edit dialog                                                  */
  /* ------------------------------------------------------------------ */

  let slotDialog;

  /* ------------------------------------------------------------------ */
  /*  Stub actions (no backend yet — mutate placeholder state directly)  */
  /* ------------------------------------------------------------------ */

  async function fetchHub() {
    loading = true;
    try {
      const res = await fetch(`${apiBase}/api/ace`);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      const hubs = data.filament_hubs ?? [];
      const found = hubs.find(h => h.id === aceId);
      if (found) hub = found;
    } catch (err) {
      if (!hub) toaster.error({ title: 'Filament Hub', description: String(err) });
    } finally {
      loading = false;
    }
  }

  async function startDrying() {
    if (!hub) return;
    dryLoading = true;
    try {
      const res = await fetch(`${apiBase}/api/ace/${aceId}/drying`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        // API expects duration in minutes; dryDuration is stored as hours
        body: JSON.stringify({ duration: dryDuration * 60, temp: dryTemp }),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      await fetchHub();
    } catch (err) {
      toaster.error({ title: 'Start drying', description: String(err) });
      // Optimistic fallback so the UI reflects intent
      hub = {
        ...hub,
        dryer: {
          status: 'drying',
          target_temp: dryTemp,
          remaining_seconds: dryDuration * 3600,
          is_active: true,
        },
      };
    } finally {
      dryLoading = false;
    }
  }

  async function stopDrying() {
    if (!hub) return;
    dryLoading = true;
    try {
      const res = await fetch(`${apiBase}/api/ace/${aceId}/drying`, { method: 'DELETE' });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      await fetchHub();
    } catch (err) {
      toaster.error({ title: 'Stop drying', description: String(err) });
      hub = {
        ...hub,
        dryer: { status: 'stop', target_temp: null, remaining_seconds: null, is_active: false },
      };
    } finally {
      dryLoading = false;
    }
  }

  async function setFilament(slotIdx, material, colorHex) {
    if (!hub) return;
    // Optimistic update
    hub = {
      ...hub,
      slots: hub.slots.map(s =>
        s.index === slotIdx
          ? { ...s, type: material, status: 'loaded', color: { rgb: hexToRgb(colorHex), hex: colorHex } }
          : s
      ),
    };
    try {
      const res = await fetch(`${apiBase}/api/ace/${aceId}/filament`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ slot: slotIdx, material, color: colorHex }),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
    } catch (err) {
      toaster.error({ title: 'Set filament', description: String(err) });
      await fetchHub(); // Revert to actual server state
    }
  }

  /** Convert "#RRGGBB" to { r, g, b }. */
  function hexToRgb(hex) {
    const v = hex.replace(/^#/, '');
    return {
      r: parseInt(v.substring(0, 2), 16),
      g: parseInt(v.substring(2, 4), 16),
      b: parseInt(v.substring(4, 6), 16),
    };
  }

  /* ------------------------------------------------------------------ */
  /*  Slot click / dialog                                                */
  /* ------------------------------------------------------------------ */

  function openSlotDialog(slot) {
    slotDialog.open(slot);
  }

  function handleDialogApply(data) {
    setFilament(data.slotIndex, data.material, data.color);
  }

  /* ------------------------------------------------------------------ */
  /*  Helpers                                                            */
  /* ------------------------------------------------------------------ */

  function slotColor(slot) {
    return slot.color?.hex ?? '#888888';
  }

  function formatRemaining(seconds) {
    if (seconds == null || seconds <= 0) return '—';
    const h = Math.floor(seconds / 3600);
    const m = Math.floor((seconds % 3600) / 60);
    return h > 0 ? `${h}h ${m}m` : `${m}m`;
  }
</script>

<div class="card card-border bg-base-100 border-base-300 w-full max-w-xl">
  <div class="card-body gap-4">
  <!-- Header -->
  <header class="flex justify-between items-center">
    <h2 class="card-title">Filament Hub</h2>
    {#if hub}
      <div class="flex items-center gap-3 text-sm opacity-75">
        {#if hub.temperature != null}
          <span class="flex items-center gap-1">
            <IconThermostat class="icon-inline" />
            {hub.temperature}°C
          </span>
        {/if}
        <span class="badge badge-outline badge-sm">
          {hub.status ?? 'unknown'}
        </span>
      </div>
    {/if}
  </header>

  {#if loading && !hub}
    <p class="text-sm opacity-60">Loading…</p>

  {:else if hub}
    <!-- Filament slots -->
    <div class="grid grid-cols-4 gap-3">
      {#each hub.slots as slot, i}
        {@const SlotIcon = SLOT_ICONS[i] ?? SLOT_ICONS[0]}
        <button
          type="button"
          class="btn btn-ghost flex flex-col h-auto py-3 gap-1"
          onclick={() => openSlotDialog(slot)}
          title="Edit Slot {(slot.index ?? i) + 1}"
        >
          <SlotIcon width={40} height={40} fill={slotColor(slot)} />
          <span class="text-xs font-medium truncate max-w-full">
            {slot.type || '—'}
          </span>
        </button>
      {/each}
    </div>

    <!-- Dryer section -->
    <div class="divider my-0"></div>
    <div class="space-y-3">
      <h3 class="text-sm font-semibold flex items-center gap-1.5">
        <IconHeat class="icon-inline" />
        Dry Box
      </h3>

      {#if hub.dryer.is_active}
        <!-- Active drying status -->
        <div role="alert" class="alert alert-warning flex-col items-start gap-2 text-sm">
          <div class="flex justify-between w-full">
            <span class="flex items-center gap-1">
              <IconThermostat class="icon-inline" />
              Target: {hub.dryer.target_temp ?? '—'}°C
            </span>
            <span class="flex items-center gap-1">
              <IconTimer class="icon-inline" />
              {formatRemaining(hub.dryer.remaining_seconds)}
            </span>
          </div>
          <button
            type="button"
            class="btn btn-error btn-sm btn-block"
            disabled={dryLoading}
            onclick={stopDrying}
          >
            <IconStop class="icon-inline" />
            Stop Drying
          </button>
        </div>
      {:else}
        <!-- Drying controls -->
        <div class="grid grid-cols-2 gap-3">
          <label class="flex flex-col gap-1">
            <span class="text-xs font-semibold">Temperature (°C)</span>
            <input class="input input-sm" type="number" min="30" max="70" bind:value={dryTemp} />
          </label>
          <label class="flex flex-col gap-1">
            <span class="text-xs font-semibold">Duration (hours)</span>
            <input class="input input-sm" type="number" min="1" max="24" bind:value={dryDuration} />
          </label>
        </div>
        <button
          type="button"
          class="btn btn-neutral btn-sm btn-block"
          disabled={dryLoading}
          onclick={startDrying}
        >
          <IconHeat class="icon-inline" />
          Start Drying
        </button>
      {/if}
    </div>
  {/if}
  </div>
</div>

<!-- Slot edit dialog -->
<FilamentSlotDialog
  bind:this={slotDialog}
  onApply={handleDialogApply}
/>
