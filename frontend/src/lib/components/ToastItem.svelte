<script>
  import { normalizeProps, useMachine } from '@zag-js/svelte';
  import * as toast from '@zag-js/toast';
  import IconError from '@material-symbols/svg-400/rounded/error-fill.svg?component';
  import IconCheckCircle from '@material-symbols/svg-400/rounded/check_circle-fill.svg?component';
  import IconWarning from '@material-symbols/svg-400/rounded/warning-fill.svg?component';
  import IconInfo from '@material-symbols/svg-400/rounded/info-fill.svg?component';

  /** @type {{ toast: toast.Options, index: number, parent: toast.GroupService }} */
  let { toast: toastData, index, parent } = $props();

  const machineProps = $derived({ ...toastData, parent, index });
  const service = useMachine(toast.machine, () => machineProps);
  const api = $derived(toast.connect(service, normalizeProps));

  const alertClass = $derived({
    error: 'alert-error',
    success: 'alert-success',
    warning: 'alert-warning',
    loading: 'alert-info',
    info: 'alert-info',
  }[api.type] ?? 'alert-info');

  const Icon = $derived({
    error: IconError,
    success: IconCheckCircle,
    warning: IconWarning,
    loading: IconInfo,
    info: IconInfo,
  }[api.type] ?? IconInfo);
</script>

<div {...api.getRootProps()} role="alert" class="alert {alertClass} alert-vertical sm:alert-horizontal">
    <Icon class="icon-inline text-2xl" />
    <div>
        {#if api.title}<h3 class="font-semibold">{api.title}</h3>{/if}
        {#if api.description}<span class="text-xs opacity-80 break-words">{api.description}</span>{/if}
    </div>
    <button class="btn btn-sm" onclick={api.dismiss}>✕</button>
</div>
