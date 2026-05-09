<script>
  import IconCounter1 from '@material-symbols/svg-200/rounded/counter_1-fill.svg?component';
  import IconCounter2 from '@material-symbols/svg-200/rounded/counter_2-fill.svg?component';
  import IconCounter3 from '@material-symbols/svg-200/rounded/counter_3-fill.svg?component';
  import IconCounter4 from '@material-symbols/svg-200/rounded/counter_4-fill.svg?component';
  import IconHeat from '@material-symbols/svg-200/rounded/heat-fill.svg?component';
  import IconStop from '@material-symbols/svg-200/rounded/stop-fill.svg?component';
  import IconThermostat from '@material-symbols/svg-200/rounded/device_thermostat-fill.svg?component';
  import IconTimer from '@material-symbols/svg-200/rounded/timer-fill.svg?component';
  import FilamentSlotDialog from './FilamentSlotDialog.svelte';

  const SLOT_ICONS = [IconCounter1, IconCounter2, IconCounter3, IconCounter4];

  /**
   * @type {{
   *   aceId?: number,
   *   apiBase?: string
   * }}
   */
  let { aceId = 0, apiBase = '' } = $props();

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
  let error = $state('');

  /* ------------------------------------------------------------------ */
  /*  Drying controls                                                    */
  /* ------------------------------------------------------------------ */

  let dryTemp = $state(50);
  let dryDuration = $state(4);       // hours
  let dryLoading = $state(false);

  /* ------------------------------------------------------------------ */
  /*  Slot‑edit dialog state                                             */
  /* ------------------------------------------------------------------ */

  let dialogOpen = $state(false);
  let dialogSlotIndex = $state(0);
  let dialogMaterial = $state('');
  let dialogColor = $state('#FFFFFF');

  /* ------------------------------------------------------------------ */
  /*  Stub actions (no backend yet — mutate placeholder state directly)  */
  /* ------------------------------------------------------------------ */

  async function fetchHub() {
    // No-op: hub is already populated with placeholder data
  }

  async function startDrying() {
    if (!hub) return;
    dryLoading = true;
    hub = {
      ...hub,
      dryer: {
        status: 'drying',
        target_temp: dryTemp,
        remaining_seconds: dryDuration * 3600,
        is_active: true,
      },
    };
    dryLoading = false;
  }

  async function stopDrying() {
    if (!hub) return;
    dryLoading = true;
    hub = {
      ...hub,
      dryer: {
        status: 'stop',
        target_temp: null,
        remaining_seconds: null,
        is_active: false,
      },
    };
    dryLoading = false;
  }

  async function setFilament(slotIdx, material, colorHex) {
    if (!hub) return;
    hub = {
      ...hub,
      slots: hub.slots.map(s =>
        s.index === slotIdx
          ? {
              ...s,
              type: material,
              status: 'loaded',
              color: {
                rgb: hexToRgb(colorHex),
                hex: colorHex,
              },
            }
          : s
      ),
    };
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
    dialogSlotIndex = slot.index ?? 0;
    dialogMaterial = slot.type ?? '';
    dialogColor = slot.color?.hex ?? '#FFFFFF';
    dialogOpen = true;
  }

  function handleDialogApply(data) {
    dialogOpen = false;
    setFilament(dialogSlotIndex, data.material, data.color);
  }

  function handleDialogCancel() {
    dialogOpen = false;
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

<div class="card card-border w-full max-w-xl">
  <div class="card-body gap-4">
  <!-- Header -->
  <header class="flex justify-between items-center">
    <h2 class="card-title">Filament Hub</h2>
    {#if hub}
      <div class="flex items-center gap-3 text-sm opacity-75">
        {#if hub.temperature != null}
          <span class="flex items-center gap-1">
            <IconThermostat width={16} height={16} fill="currentColor" />
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
  {:else if error && !hub}
    <div role="alert" class="alert alert-error text-sm">{error}</div>
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
        <IconHeat width={18} height={18} fill="currentColor" />
        Filament Drying
      </h3>

      {#if hub.dryer.is_active}
        <!-- Active drying status -->
        <div role="alert" class="alert alert-warning flex-col items-start gap-2 text-sm">
          <div class="flex justify-between w-full">
            <span class="flex items-center gap-1">
              <IconThermostat width={14} height={14} fill="currentColor" />
              Target: {hub.dryer.target_temp ?? '—'}°C
            </span>
            <span class="flex items-center gap-1">
              <IconTimer width={14} height={14} fill="currentColor" />
              {formatRemaining(hub.dryer.remaining_seconds)}
            </span>
          </div>
          <button
            type="button"
            class="btn btn-error btn-sm btn-block"
            disabled={dryLoading}
            onclick={stopDrying}
          >
            <IconStop width={16} height={16} fill="currentColor" />
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
          <IconHeat width={16} height={16} fill="currentColor" />
          Start Drying
        </button>
      {/if}
    </div>

    {#if error}
      <div role="alert" class="alert alert-error text-sm">{error}</div>
    {/if}
  {/if}
  </div>
</div>

<!-- Slot edit dialog -->
<FilamentSlotDialog
  open={dialogOpen}
  slotIndex={dialogSlotIndex}
  material={dialogMaterial}
  color={dialogColor}
  onApply={handleDialogApply}
  onCancel={handleDialogCancel}
/>
