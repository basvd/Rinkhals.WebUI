<script>
  import { normalizeProps, useMachine } from '@zag-js/svelte';
  import * as toast from '@zag-js/toast';
  import { toaster } from '@/lib/toast';
  import ToastItem from './ToastItem.svelte';

  const service = useMachine(toast.group.machine, () => ({
    id: 'toast-group',
    store: toaster,
  }));

  const api = $derived(toast.group.connect(service, normalizeProps));
</script>

<div {...api.getGroupProps()} class="toast z-50 w-72">
  {#each api.getToasts() as t, index (t.id)}
    <ToastItem toast={t} {index} parent={service} />
  {/each}
</div>

<style>
  :global([data-part="root"]) {
    translate: var(--x) var(--y);
    scale: var(--scale);
    z-index: var(--z-index);
    /* height: var(--height); */
    opacity: var(--opacity);
    will-change: translate, opacity, scale;
    transition:
      translate 400ms,
      scale 400ms,
      opacity 400ms;
    transition-timing-function: cubic-bezier(0.21, 1.02, 0.73, 1);
  }

  :global([data-part="root"][data-state="closed"]) {
    transition:
      translate 400ms,
      scale 400ms,
      opacity 200ms;
    transition-timing-function: cubic-bezier(0.06, 0.71, 0.55, 1);
  }
</style>
