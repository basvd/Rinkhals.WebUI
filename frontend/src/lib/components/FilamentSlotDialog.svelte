<script>
  import { Dialog } from 'bits-ui';
  import ColorPicker from './ColorPicker.svelte';

  /**
   * @type {{
   *   open: boolean,
   *   slotIndex: number,
   *   material: string,
   *   color: string,
   *   onApply: (data: { material: string, color: string }) => void,
   *   onCancel: () => void
   * }}
   */
  let { open = false, slotIndex = 0, material = '', color = '#FFFFFF', onApply, onCancel } = $props();

  // Standard filament types known to Orca Slicer, retrieved from:
  // https://github.com/OrcaSlicer/OrcaSlicer/tree/main/resources/profiles/OrcaFilamentLibrary/filament/base
  const FILAMENT_TYPES = [
    'ABS', 'ASA', 'BVOH', 'CoPE', 'EVA', 'HIPS', 'PA', 'PAHT',
    'PC', 'PCTG', 'PE', 'PETG', 'PHA', 'PLA', 'PP', 'PPA-CF',
    'PPS', 'PVA', 'SBS', 'TPU', 'Custom'
  ];

  // Local editing state — synced from props via $effect
  let editMaterial = $state('PLA');
  let editColor = $state('#FFFFFF');
  let customMaterial = $state('');
  let isCustom = $state(false);

  // Sync local state when the dialog opens with new props
  let prevOpen = false;
  $effect(() => {
    if (open && !prevOpen) {
      // Dialog just opened — snapshot current props
      const knownType = FILAMENT_TYPES.find(t => t === material);
      if (knownType && knownType !== 'Custom') {
        editMaterial = knownType;
        customMaterial = '';
        isCustom = false;
      } else if (material) {
        editMaterial = 'Custom';
        customMaterial = material;
        isCustom = true;
      } else {
        editMaterial = 'PLA';
        customMaterial = '';
        isCustom = false;
      }
      editColor = color || '#FFFFFF';
    }
    prevOpen = open;
  });

  function handleTypeChange(e) {
    editMaterial = e.target.value;
    isCustom = editMaterial === 'Custom';
    if (!isCustom) customMaterial = '';
  }

  function handleApply() {
    const finalMaterial = isCustom ? (customMaterial.trim() || 'Custom') : editMaterial;
    onApply?.({ material: finalMaterial, color: editColor });
  }

  function handleCancel() {
    onCancel?.();
  }

  function handleColorChange(hex) {
    editColor = hex;
  }
</script>

<Dialog.Root bind:open>
  <Dialog.Portal>
    <Dialog.Overlay class="fixed inset-0 z-40 bg-black/50" />
    <Dialog.Content
      class="fixed left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 z-50 card bg-base-100 w-full max-w-lg shadow-2xl overflow-y-auto max-h-[calc(100dvh-2rem)]"
      interactOutsideBehavior="ignore"
      escapeKeydownBehavior="ignore"
    >
      <div class="card-body">

        <Dialog.Title class="text-lg font-bold">Edit Filament Slot {slotIndex + 1}</Dialog.Title>

          <!-- Filament type selector -->
          <fieldset class="fieldset">
            <legend class="fieldset-legend">Filament Type</legend>
            <select class="select select-sm w-full" value={editMaterial} onchange={handleTypeChange}>
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

          <!-- Actions -->
          <div class="card-actions justify-end pt-2">
            <button type="button" class="btn btn-ghost btn-sm" onclick={handleCancel}>Cancel</button>
            <button type="button" class="btn btn-primary btn-sm" onclick={handleApply}>Apply</button>
          </div>
      </div>
    </Dialog.Content>
  </Dialog.Portal>
</Dialog.Root>
