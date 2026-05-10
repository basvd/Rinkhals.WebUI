<script>
  import IconClose from '@material-symbols/svg-400/rounded/close-fill.svg?component';
  import IconWarning from '@material-symbols/svg-400/rounded/warning-fill.svg?component';

  /**
   * @type {{
   *   title?: string,
   *   message?: string,
   *   confirmLabel?: string,
   *   confirmClass?: string,
   *   loading?: boolean,
   *   onConfirm?: () => void
   * }}
   */
  let {
    title = 'Are you sure?',
    message = '',
    confirmLabel = 'Confirm',
    confirmClass = '',
    loading = false,
    onConfirm,
  } = $props();

  let isOpen = $state(false);

  /** @type {HTMLDialogElement} */
  let dialogEl;

  export function open() {
    isOpen = true;
    dialogEl.showModal();
  }

  export function close() {
    dialogEl.close();
  }
</script>

<dialog
  bind:this={dialogEl}
  class="modal"
  oncancel={(e) => e.preventDefault()}
  onclose={() => (isOpen = false)}
>
  {#if isOpen}
    <div class="modal-box">
    <h3 class="font-bold text-lg flex items-center gap-2">
      <IconWarning width={20} height={20} fill="currentColor" class="text-warning shrink-0" />
      {title}
    </h3>

    {#if message}
      <p class="py-2 text-sm text-base-content/80">{message}</p>
    {/if}

    <div class="modal-action">
      <form method="dialog">
        <button class="btn btn-ghost btn-sm" disabled={loading}>Cancel</button>
      </form>
      <button
        type="button"
        class="btn btn-sm {confirmClass}"
        disabled={loading}
        onclick={onConfirm}
      >
        {#if loading}
          <span class="loading loading-spinner loading-xs"></span>
        {/if}
        {confirmLabel}
      </button>
    </div>

    <form method="dialog" class="absolute top-3 right-3">
      <button class="btn btn-ghost btn-xs btn-circle" disabled={loading}>
        <IconClose width={16} height={16} fill="currentColor" />
      </button>
    </form>
  </div>
  {/if}
</dialog>
