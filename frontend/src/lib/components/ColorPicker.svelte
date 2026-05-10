<script>
  import * as colorPicker from '@zag-js/color-picker';
  import { normalizeProps, useMachine } from '@zag-js/svelte';

  /** @type {{ value?: string, onchange?: (hex: string) => void }} */
  let { value = '#7e5b7f', onchange } = $props();

  const id = $props.id();

  const service = useMachine(colorPicker.machine, {
    id,
    get defaultValue() { return colorPicker.parse(value); },
    defaultFormat: 'rgba',
    inline: true,
    onValueChange(details) {
      onchange?.(details.value.toString('hex'));
    },
  });

  const api = $derived(colorPicker.connect(service, normalizeProps));

  let hex = $derived(api.value.toString('hex'));

  // Sampled colors from https://filamentcolors.xyz
  const PRESETS = [
    // White / Grey / Black
    '#E3E5DE', '#B9C2C2', '#838080', '#404141',
    // Red / Orange / Yellow
    '#CB3636', '#94322B', '#EB5403', '#E87336',
    '#F0CF3F', '#D3C61B',
    // Green / Blue
    '#54D542', '#008A58', '#224B36', '#3CA4B8',
    '#065AA1', '#19397C',
    // Brown / Purple / Pink
    '#957760', '#6E4D44', '#6F5793', '#59378A',
    '#CF6398', '#E1347D', '#F291A4', '#CD70A5',
  ];
</script>

<div {...api.getRootProps()} class="color-picker flex flex-col gap-3 select-none w-full">
  <!-- Top row: SV area + hue slider + inputs -->
  <div class="flex flex-row gap-3">
    <!-- Saturation / Value area -->
    <div {...api.getAreaProps()} class="cp-area flex-1 rounded-sm">
      <div {...api.getAreaBackgroundProps()} class="cp-area-bg rounded-sm"></div>
      <div {...api.getAreaThumbProps()} class="cp-area-thumb"></div>
    </div>

    <!-- Hue slider (vertical) -->
    <div {...api.getChannelSliderProps({ channel: 'hue', orientation: 'vertical' })} class="cp-hue-slider rounded-sm">
      <div {...api.getChannelSliderTrackProps({ channel: 'hue', orientation: 'vertical' })} class="cp-hue-track rounded-sm"></div>
      <div {...api.getChannelSliderThumbProps({ channel: 'hue', orientation: 'vertical' })} class="cp-hue-thumb"></div>
    </div>

    <!-- Right column: preview + inputs -->
    <div class="grid gap-x-3 gap-y-1.5 items-center px-1.5" style="grid-template-columns: auto minmax(0, 6rem);">
      <!-- Color preview -->
      <div
        class="rounded-sm col-span-2 -mx-1.5"
        style="background:{hex};height:80px;"
      ></div>

      <!-- RGB + Hex inputs -->
      <span class="text-xs font-bold">R</span>
      <input {...api.getChannelInputProps({ channel: 'red' })}
             class="input input-xs" />
      <span class="text-xs font-bold">G</span>
      <input {...api.getChannelInputProps({ channel: 'green' })}
             class="input input-xs" />
      <span class="text-xs font-bold">B</span>
      <input {...api.getChannelInputProps({ channel: 'blue' })}
             class="input input-xs" />
      <span class="text-xs font-bold">#</span>
      <input {...api.getChannelInputProps({ channel: 'hex' })}
             class="input input-xs" />
    </div>
  </div>

  <!-- Presets -->
  <div {...api.getSwatchGroupProps()} class="flex flex-wrap justify-between gap-1.5 overflow-hidden p-1 -m-1 max-h-7">
    {#each PRESETS as preset}
      <button {...api.getSwatchTriggerProps({ value: preset })} class="cursor-pointer border-none p-0 rounded">
        <div {...api.getSwatchProps({ value: preset })} class="w-5 h-5 rounded border border-black/10 data-[state=checked]:ring-2 ring-current ring-offset-2 ring-offset-base-100"></div>
      </button>
    {/each}
  </div>
</div>

<style>
  /* ---- SV area ---- */
  .cp-area {
    position: relative;
    min-width: 120px;
    min-height: 160px;
    cursor: crosshair;
  }

  .cp-area-bg {
    width: 100%;
    height: 100%;
    overflow: hidden;
  }

  .cp-area-thumb {
    width: 12px;
    height: 12px;
    border: 2px solid #fff;
    border-radius: 50%;
    box-shadow: 0 0 3px rgba(0,0,0,0.6);
    /* Zag sets: position, left, top, transform, background */
  }

  /* ---- Hue slider (vertical) ---- */
  .cp-hue-slider {
    position: relative;
    width: 20px;
    min-height: 160px;
    cursor: pointer;
  }

  .cp-hue-track {
    width: 100%;
    height: 100%;
    overflow: hidden;
    transform: scaleY(-1); /* flip gradient to match thumb direction */
  }

  .cp-hue-thumb {
    width: calc(100% + 6px);
    height: 6px;
    border: 2px solid #fff;
    border-radius: 2px;
    box-shadow: 0 0 3px rgba(0,0,0,0.6);
    transform: translate(-50%, -50%);
  }

</style>
