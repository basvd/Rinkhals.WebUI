<script>
  import ColorPicker from '../ColorPicker.svelte';

  /**
   * @type {{
   *   onApply?: (data: { slotIndex: number, material: string, color: string }) => void,
   * }}
   */
  let { onApply } = $props();

  // Standard filament types known to Orca Slicer, retrieved from:
  // https://github.com/OrcaSlicer/OrcaSlicer/tree/main/resources/profiles/OrcaFilamentLibrary/filament/base
  const FILAMENT_TYPES = [
    'ABS', 'ASA', 'BVOH', 'CoPE', 'EVA', 'HIPS', 'PA', 'PAHT',
    'PC', 'PCTG', 'PE', 'PETG', 'PHA', 'PLA', 'PP', 'PPA-CF',
    'PPS', 'PVA', 'SBS', 'TPU', 'Custom'
  ];

  let isOpen = $state(false);
  let slotIndex = $state(0);
  let editMaterial = $state('PLA');
  let editColor = $state('#FFFFFF');
  let customMaterial = $state('');
  let isCustom = $state(false);

  /** @type {HTMLDialogElement} */
  let dialogEl;

  export function open(slot) {
    slotIndex = slot.index ?? 0;
    const knownType = FILAMENT_TYPES.find(t => t === slot.type);
    if (knownType && knownType !== 'Custom') {
      editMaterial = knownType;
      customMaterial = '';
      isCustom = false;
    } else if (slot.type) {
      editMaterial = 'Custom';
      customMaterial = slot.type;
      isCustom = true;
    } else {
      editMaterial = 'PLA';
      customMaterial = '';
      isCustom = false;
    }
    editColor = slot.color?.hex ?? '#FFFFFF';
    isOpen = true;
    dialogEl.showModal();
  }

  function handleTypeChange() {
    isCustom = editMaterial === 'Custom';
    if (!isCustom) customMaterial = '';
  }

  function handleClose() {
    if (dialogEl.returnValue === 'apply') {
      const finalMaterial = isCustom ? (customMaterial.trim() || 'Custom') : editMaterial;
      onApply?.({ slotIndex, material: finalMaterial, color: editColor });
    }
    isOpen = false;
  }

  function handleColorChange(hex) {
    editColor = hex;
  }
</script>

<dialog
  bind:this={dialogEl}
  class="modal"
  onclose={handleClose}
>
  {#if isOpen}
    <form method="dialog" class="modal-box max-h-[calc(100dvh-2rem)] overflow-y-auto">
      <h3 class="font-bold text-lg">Filament Slot {slotIndex + 1}</h3>

      <!-- Filament type selector -->
      <fieldset class="fieldset">
        <legend class="fieldset-legend">Filament Type</legend>
        <select class="select select-sm w-full" bind:value={editMaterial} onchange={handleTypeChange}>
          {#each FILAMENT_TYPES as ft}
            <option value={ft}>{ft}</option>
          {/each}
        </select>
      </fieldset>

      <!-- Custom type field (shown when "Custom" is chosen) -->
      {#if isCustom}
        <fieldset class="fieldset">
          <legend class="fieldset-legend">Custom Type Name</legend>
          <input
            class="input input-sm w-full"
            type="text"
            placeholder="Enter custom filament type…"
            bind:value={customMaterial}
          />
        </fieldset>
      {/if}

      <!-- Color picker -->
      <fieldset class="fieldset">
        <legend class="fieldset-legend">Filament Color</legend>
        <ColorPicker value={editColor} onchange={handleColorChange} />
      </fieldset>

      <div class="modal-action">
        <button type="submit" class="btn btn-ghost btn-sm">Cancel</button>
        <button type="submit" value="apply" class="btn btn-primary btn-sm">Apply</button>
      </div>
    </form>
  {/if}
</dialog>
